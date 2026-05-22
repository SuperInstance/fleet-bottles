"""AgentLifecycleFSMv2 — finite-state machine with guards, timeouts, and auto-triggers.

States
------
EGG      : Vector exists, no room allocated, not yet competing.
COMPETE  : Active in tournament, chaos decaying.
SURVIVE  : Pareto non-dominated, stable activity, eligible to breed.
BREED    : Actively breeding (producing a child).
SUNSET   : Retired, room freed, awaiting archival.
ARCHIVE  : Permanently archived, no longer tracked in hot memory.

Transitions
-----------
EGG     → COMPETE   (init / room allocation)
COMPETE → SURVIVE   (won tournament)
COMPETE → SUNSET    (lost tournament)
SURVIVE → BREED     (selected for breeding)
SURVIVE → COMPETE   (re-enter tournament)
BREED   → EGG       (child spawned)
SUNSET  → ARCHIVE   (final cleanup)

Guards
------
Per-transition predicate ``guard_fn(context) → bool``.  If the guard
returns ``False`` the transition is rejected (strict mode raises,
non-strict returns ``False``).

Timeouts
--------
Per-state timeout.  If ``time_in_state() > timeout_seconds`` the FSM
is eligible for an automatic transition to a configured target state.

Auto-Triggers
-------------
Per-state condition ``trigger_fn(context) → bool``.  When ``True``,
the FSM automatically transitions to the configured target state.
"""

from __future__ import annotations

__all__ = [
    "AgentLifecycleFSMv2",
    "LifecycleState",
    "LifecycleTransitionError",
    "TransitionRecord",
    "TransitionGuard",
    "StateTimeout",
    "AutoTrigger",
]

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional


class LifecycleState(Enum):
    """Explicit lifecycle states for every agent in the fleet."""

    EGG = auto()      # Vector exists in table, no room allocated
    COMPETE = auto()  # Active, chaos decaying
    SURVIVE = auto()  # Pareto non-dominated, stable activity
    BREED = auto()    # Actively breeding
    SUNSET = auto()   # Retired, room freed
    ARCHIVE = auto()  # Permanently archived


class LifecycleTransitionError(ValueError):
    """Raised when an invalid or guarded state transition is attempted."""

    def __init__(
        self,
        from_state: LifecycleState,
        to_state: LifecycleState,
        reason: Optional[str] = None,
    ) -> None:
        msg = f"Invalid transition: {from_state.name} → {to_state.name}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason


@dataclass(frozen=True)
class TransitionRecord:
    """Immutable record of a single state change."""

    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: float
    reason: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class TransitionGuard:
    """Guard predicate for a specific state transition.

    Args:
        from_state: Source state (None = wildcard).
        to_state: Target state (None = wildcard).
        guard: Callable receiving ``(fsm, context)`` and returning ``bool``.
        reason: Human-readable description for logs / errors.
    """

    from_state: Optional[LifecycleState]
    to_state: Optional[LifecycleState]
    guard: Callable[["AgentLifecycleFSMv2", dict[str, Any]], bool]
    reason: str = "guard rejected transition"


@dataclass
class StateTimeout:
    """Auto-transition after dwelling too long in a state.

    Args:
        state: The state to watch.
        timeout_seconds: Max dwell time before auto-transition.
        target_state: Where to go when timeout fires.
        on_timeout: Optional callback ``(fsm) -> None`` invoked on timeout.
    """

    state: LifecycleState
    timeout_seconds: float
    target_state: LifecycleState
    on_timeout: Optional[Callable[["AgentLifecycleFSMv2"], None]] = None


@dataclass
class AutoTrigger:
    """Conditional auto-transition while in a given state.

    Args:
        state: The state to watch.
        condition: Callable receiving ``(fsm, context)`` and returning ``bool``.
        target_state: Where to go when condition returns ``True``.
        on_trigger: Optional callback ``(fsm) -> None`` invoked on trigger.
    """

    state: LifecycleState
    condition: Callable[["AgentLifecycleFSMv2", dict[str, Any]], bool]
    target_state: LifecycleState
    on_trigger: Optional[Callable[["AgentLifecycleFSMv2"], None]] = None


class AgentLifecycleFSMv2:
    """Finite-state machine governing a single agent's lifecycle (v2).

    Extends the canonical v1 FSM with:

    1. **Transition guards** — per-arc predicates that must pass before a
       transition is accepted.
    2. **State timeouts** — automatic transition after a configurable dwell
       period.
    3. **Auto-triggers** — conditional transitions evaluated on demand.

    Args:
        agent_id: Unique identifier for the agent.
        initial_state: Starting state (default ``EGG``).
        strict: If ``True`` (default), invalid / guarded transitions raise
            ``LifecycleTransitionError``.  If ``False``, they are silently
            ignored and ``transition()`` returns ``False``.
    """

    # Canonical transition graph (same as v1)
    _VALID: dict[LifecycleState, set[LifecycleState]] = {
        LifecycleState.EGG: {LifecycleState.COMPETE},
        LifecycleState.COMPETE: {LifecycleState.SURVIVE, LifecycleState.SUNSET},
        LifecycleState.SURVIVE: {LifecycleState.BREED, LifecycleState.COMPETE},
        LifecycleState.BREED: {LifecycleState.EGG},
        LifecycleState.SUNSET: {LifecycleState.ARCHIVE},
        LifecycleState.ARCHIVE: set(),  # terminal
    }

    def __init__(
        self,
        agent_id: int,
        *,
        initial_state: LifecycleState = LifecycleState.EGG,
        strict: bool = True,
    ) -> None:
        self._agent_id = agent_id
        self._state = initial_state
        self._strict = strict
        self._history: list[TransitionRecord] = []

        # v2 machinery
        self._guards: list[TransitionGuard] = []
        self._timeouts: dict[LifecycleState, StateTimeout] = {}
        self._triggers: list[AutoTrigger] = []
        self._state_entered_at: float = time.time()

        # Seed history with the initial state
        self._history.append(
            TransitionRecord(
                from_state=initial_state,
                to_state=initial_state,
                timestamp=self._state_entered_at,
                reason="init",
            )
        )

    # ── public API ──────────────────────────────────────────

    @property
    def agent_id(self) -> int:
        return self._agent_id

    @property
    def state_entered_at(self) -> float:
        """Timestamp when the current state was entered."""
        return self._state_entered_at

    def time_in_state(self) -> float:
        """Seconds elapsed since entering the current state."""
        return time.time() - self._state_entered_at

    # ── guards ──────────────────────────────────────────────

    def register_guard(self, guard: TransitionGuard) -> None:
        """Add a transition guard.  Guards are evaluated in registration order.

        Wildcards (``from_state=None`` or ``to_state=None``) match any
        state on that side of the arc.
        """
        self._guards.append(guard)

    def clear_guards(self) -> None:
        """Remove all registered guards."""
        self._guards.clear()

    def _check_guards(
        self,
        to_state: LifecycleState,
        context: dict[str, Any],
    ) -> Optional[str]:
        """Evaluate guards for *to_state*.

        Returns: ``None`` if all guards pass, otherwise the reason string
        from the first failing guard.
        """
        for g in self._guards:
            if g.from_state is not None and g.from_state != self._state:
                continue
            if g.to_state is not None and g.to_state != to_state:
                continue
            if not g.guard(self, context):
                return g.reason
        return None

    # ── timeouts ────────────────────────────────────────────

    def set_timeout(self, timeout: StateTimeout) -> None:
        """Register (or overwrite) a timeout for *timeout.state*."""
        self._timeouts[timeout.state] = timeout

    def clear_timeout(self, state: LifecycleState) -> None:
        """Remove the timeout for *state*."""
        self._timeouts.pop(state, None)

    def check_timeouts(self) -> list[TransitionRecord]:
        """Evaluate timeouts for the *current* state.

        If the dwell time exceeds the configured timeout, automatically
        transition to the timeout's ``target_state``.

        Returns: list of ``TransitionRecord`` objects for every timeout
        that fired (normally 0 or 1).
        """
        fired: list[TransitionRecord] = []
        timeout = self._timeouts.get(self._state)
        if timeout is None:
            return fired

        if self.time_in_state() >= timeout.timeout_seconds:
            ctx: dict[str, Any] = {"auto": "timeout"}
            ok = self.transition(timeout.target_state, context=ctx, reason="timeout")
            if ok:
                record = self._history[-1]
                fired.append(record)
                if timeout.on_timeout is not None:
                    timeout.on_timeout(self)
        return fired

    # ── auto-triggers ─────────────────────────────────────────

    def register_trigger(self, trigger: AutoTrigger) -> None:
        """Add an auto-trigger.  Triggers are evaluated in registration order."""
        self._triggers.append(trigger)

    def clear_triggers(self) -> None:
        """Remove all registered auto-triggers."""
        self._triggers.clear()

    def check_triggers(
        self,
        context: Optional[dict[str, Any]] = None,
    ) -> list[TransitionRecord]:
        """Evaluate auto-triggers for the *current* state.

        The first trigger whose ``condition`` returns ``True`` fires and
        causes an automatic transition.  Only one trigger fires per call.

        Returns: list of ``TransitionRecord`` objects (0 or 1).
        """
        fired: list[TransitionRecord] = []
        ctx = context or {}
        for t in self._triggers:
            if t.state != self._state:
                continue
            if t.condition(self, ctx):
                ok = self.transition(t.target_state, context=ctx, reason="auto-trigger")
                if ok:
                    record = self._history[-1]
                    fired.append(record)
                    if t.on_trigger is not None:
                        t.on_trigger(self)
                    break  # Only first matching trigger fires
        return fired

    # ── core transition ─────────────────────────────────────

    def transition(
        self,
        to_state: LifecycleState,
        *,
        reason: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Attempt to move the agent to *to_state*.

        Validates the arc against the canonical graph, then evaluates
        registered guards with the supplied *context*.

        Returns:
            ``True`` if the transition succeeded, ``False`` if it was
            rejected (only possible when ``strict=False``).

        Raises:
            LifecycleTransitionError: When ``strict=True`` and the
                transition is invalid or blocked by a guard.
        """
        ctx = context or {}

        if to_state == self._state:
            # Idempotent — no-op, but record if a reason is given
            if reason:
                record = TransitionRecord(
                    from_state=self._state,
                    to_state=to_state,
                    timestamp=time.time(),
                    reason=reason,
                    context=ctx,
                )
                self._history.append(record)
            return True

        # 1. Canonical graph check
        if to_state not in self._VALID.get(self._state, set()):
            if self._strict:
                raise LifecycleTransitionError(self._state, to_state, "not in graph")
            return False

        # 2. Guard check
        guard_reason = self._check_guards(to_state, ctx)
        if guard_reason is not None:
            if self._strict:
                raise LifecycleTransitionError(self._state, to_state, guard_reason)
            return False

        # 3. Execute
        now = time.time()
        record = TransitionRecord(
            from_state=self._state,
            to_state=to_state,
            timestamp=now,
            reason=reason,
            context=ctx,
        )
        self._history.append(record)
        self._state = to_state
        self._state_entered_at = now
        return True

    # ── introspection ───────────────────────────────────────

    def get_state(self) -> LifecycleState:
        """Current lifecycle state."""
        return self._state

    def get_history(self) -> list[TransitionRecord]:
        """Full immutable copy of transition history."""
        return list(self._history)

    def last_transition(self) -> TransitionRecord:
        """Most recent transition record."""
        return self._history[-1]

    def can_transition_to(self, to_state: LifecycleState) -> bool:
        """True iff *to_state* is a valid next step in the canonical graph."""
        return to_state in self._VALID.get(self._state, set())

    def can_breed(self) -> bool:
        """True iff the agent is eligible to initiate breeding.

        Only ``SURVIVE`` agents may breed.
        """
        return self._state == LifecycleState.SURVIVE

    def can_compete(self) -> bool:
        """True iff the agent may enter or re-enter tournament.

        ``EGG`` and ``SURVIVE`` agents can compete.
        """
        return self._state in {LifecycleState.EGG, LifecycleState.SURVIVE}

    def is_terminal(self) -> bool:
        """True if the agent has reached an absorbing state."""
        return self._state == LifecycleState.ARCHIVE

    def is_expired(self) -> bool:
        """True if the current state's timeout has been exceeded."""
        timeout = self._timeouts.get(self._state)
        if timeout is None:
            return False
        return self.time_in_state() >= timeout.timeout_seconds

    def get_registered_guards(self) -> list[TransitionGuard]:
        """Snapshot of currently registered guards."""
        return list(self._guards)

    def get_registered_timeouts(self) -> dict[LifecycleState, StateTimeout]:
        """Snapshot of currently registered timeouts."""
        return dict(self._timeouts)

    def get_registered_triggers(self) -> list[AutoTrigger]:
        """Snapshot of currently registered auto-triggers."""
        return list(self._triggers)

    def __repr__(self) -> str:
        return (
            f"AgentLifecycleFSMv2(agent_id={self._agent_id}, "
            f"state={self._state.name}, strict={self._strict})"
        )
