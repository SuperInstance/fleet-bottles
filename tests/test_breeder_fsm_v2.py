"""Tests for AgentLifecycleFSMv2.

Covers the canonical transition graph, guards, timeouts, auto-triggers,
and history immutability.
"""

from __future__ import annotations

import time

import pytest

from swarm.breeder_fsm_v2 import (
    AgentLifecycleFSMv2,
    AutoTrigger,
    LifecycleState,
    LifecycleTransitionError,
    StateTimeout,
    TransitionGuard,
    TransitionRecord,
)


# ── Valid Transitions (canonical graph) ─────────────────────

class TestValidTransitions:
    """Every valid arc in the canonical graph."""

    def test_egg_to_compete(self):
        fsm = AgentLifecycleFSMv2(agent_id=1)
        assert fsm.get_state() == LifecycleState.EGG
        fsm.transition(LifecycleState.COMPETE, reason="init")
        assert fsm.get_state() == LifecycleState.COMPETE

    def test_compete_to_survive(self):
        fsm = AgentLifecycleFSMv2(agent_id=2)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SURVIVE, reason="tournament_win")
        assert fsm.get_state() == LifecycleState.SURVIVE

    def test_compete_to_sunset(self):
        fsm = AgentLifecycleFSMv2(agent_id=3)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SUNSET, reason="tournament_loss")
        assert fsm.get_state() == LifecycleState.SUNSET

    def test_survive_to_breed(self):
        fsm = AgentLifecycleFSMv2(agent_id=4)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SURVIVE)
        fsm.transition(LifecycleState.BREED, reason="selected")
        assert fsm.get_state() == LifecycleState.BREED

    def test_survive_to_compete(self):
        fsm = AgentLifecycleFSMv2(agent_id=5)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SURVIVE)
        fsm.transition(LifecycleState.COMPETE, reason="re_enter")
        assert fsm.get_state() == LifecycleState.COMPETE

    def test_breed_to_egg(self):
        fsm = AgentLifecycleFSMv2(agent_id=6)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SURVIVE)
        fsm.transition(LifecycleState.BREED)
        fsm.transition(LifecycleState.EGG, reason="child_spawned")
        assert fsm.get_state() == LifecycleState.EGG

    def test_sunset_to_archive(self):
        fsm = AgentLifecycleFSMv2(agent_id=7)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SUNSET)
        fsm.transition(LifecycleState.ARCHIVE, reason="final_cleanup")
        assert fsm.get_state() == LifecycleState.ARCHIVE


# ── Invalid Transitions ───────────────────────────────────────

class TestInvalidTransitions:
    """Invalid arcs must raise in strict mode."""

    def test_egg_to_sunset_raises(self):
        fsm = AgentLifecycleFSMv2(agent_id=10)
        with pytest.raises(LifecycleTransitionError) as exc:
            fsm.transition(LifecycleState.SUNSET)
        assert exc.value.from_state == LifecycleState.EGG
        assert exc.value.to_state == LifecycleState.SUNSET

    def test_egg_to_archive_raises(self):
        fsm = AgentLifecycleFSMv2(agent_id=11)
        with pytest.raises(LifecycleTransitionError):
            fsm.transition(LifecycleState.ARCHIVE)

    def test_compete_to_breed_raises(self):
        fsm = AgentLifecycleFSMv2(agent_id=12)
        fsm.transition(LifecycleState.COMPETE)
        with pytest.raises(LifecycleTransitionError):
            fsm.transition(LifecycleState.BREED)

    def test_archive_no_outgoing(self):
        fsm = AgentLifecycleFSMv2(agent_id=13)
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SUNSET)
        fsm.transition(LifecycleState.ARCHIVE)
        with pytest.raises(LifecycleTransitionError):
            fsm.transition(LifecycleState.EGG)

    def test_non_strict_ignores_invalid(self):
        fsm = AgentLifecycleFSMv2(agent_id=14, strict=False)
        ok = fsm.transition(LifecycleState.SUNSET)
        assert ok is False
        assert fsm.get_state() == LifecycleState.EGG


# ── Transition Guards ───────────────────────────────────────

class TestTransitionGuards:
    """Guards block or allow transitions based on runtime predicates."""

    def test_guard_blocks_transition_strict(self):
        fsm = AgentLifecycleFSMv2(agent_id=20)
        guard = TransitionGuard(
            from_state=LifecycleState.EGG,
            to_state=LifecycleState.COMPETE,
            guard=lambda fsm, ctx: False,
            reason="room_not_ready",
        )
        fsm.register_guard(guard)
        with pytest.raises(LifecycleTransitionError) as exc:
            fsm.transition(LifecycleState.COMPETE)
        assert "room_not_ready" in str(exc.value)

    def test_guard_blocks_transition_non_strict(self):
        fsm = AgentLifecycleFSMv2(agent_id=21, strict=False)
        guard = TransitionGuard(
            from_state=LifecycleState.EGG,
            to_state=LifecycleState.COMPETE,
            guard=lambda fsm, ctx: False,
            reason="room_not_ready",
        )
        fsm.register_guard(guard)
        ok = fsm.transition(LifecycleState.COMPETE)
        assert ok is False
        assert fsm.get_state() == LifecycleState.EGG

    def test_guard_allows_transition(self):
        fsm = AgentLifecycleFSMv2(agent_id=22)
        guard = TransitionGuard(
            from_state=LifecycleState.EGG,
            to_state=LifecycleState.COMPETE,
            guard=lambda fsm, ctx: True,
            reason="should_pass",
        )
        fsm.register_guard(guard)
        fsm.transition(LifecycleState.COMPETE)
        assert fsm.get_state() == LifecycleState.COMPETE

    def test_guard_receives_context(self):
        fsm = AgentLifecycleFSMv2(agent_id=23)
        received: dict[str, object] = {}

        def capture_ctx(fsm, ctx):
            received.update(ctx)
            return True

        guard = TransitionGuard(
            from_state=None,  # wildcard
            to_state=None,    # wildcard
            guard=capture_ctx,
            reason="capture",
        )
        fsm.register_guard(guard)
        fsm.transition(LifecycleState.COMPETE, context={"room_id": 42})
        assert received.get("room_id") == 42

    def test_guard_only_matches_specific_arc(self):
        fsm = AgentLifecycleFSMv2(agent_id=24)
        fsm.transition(LifecycleState.COMPETE)
        # Guard only on EGG→COMPETE, should not affect COMPETE→SURVIVE
        guard = TransitionGuard(
            from_state=LifecycleState.EGG,
            to_state=LifecycleState.COMPETE,
            guard=lambda fsm, ctx: False,
            reason="egg_guard",
        )
        fsm.register_guard(guard)
        fsm.transition(LifecycleState.SURVIVE)
        assert fsm.get_state() == LifecycleState.SURVIVE

    def test_multiple_guards_evaluated_in_order(self):
        fsm = AgentLifecycleFSMv2(agent_id=25)
        calls: list[int] = []

        def g1(fsm, ctx):
            calls.append(1)
            return True

        def g2(fsm, ctx):
            calls.append(2)
            return False

        fsm.register_guard(
            TransitionGuard(
                from_state=None,
                to_state=None,
                guard=g1,
                reason="g1",
            )
        )
        fsm.register_guard(
            TransitionGuard(
                from_state=None,
                to_state=None,
                guard=g2,
                reason="g2",
            )
        )
        with pytest.raises(LifecycleTransitionError):
            fsm.transition(LifecycleState.COMPETE)
        assert calls == [1, 2]

    def test_clear_guards(self):
        fsm = AgentLifecycleFSMv2(agent_id=26)
        guard = TransitionGuard(
            from_state=LifecycleState.EGG,
            to_state=LifecycleState.COMPETE,
            guard=lambda fsm, ctx: False,
            reason="block",
        )
        fsm.register_guard(guard)
        fsm.clear_guards()
        fsm.transition(LifecycleState.COMPETE)
        assert fsm.get_state() == LifecycleState.COMPETE

    def test_can_transition_to_ignores_guards(self):
        fsm = AgentLifecycleFSMv2(agent_id=27)
        fsm.register_guard(
            TransitionGuard(
                from_state=LifecycleState.EGG,
                to_state=LifecycleState.COMPETE,
                guard=lambda fsm, ctx: False,
                reason="block",
            )
        )
        # can_transition_to only checks the graph, not guards
        assert fsm.can_transition_to(LifecycleState.COMPETE) is True


# ── State Timeouts ────────────────────────────────────────────

class TestStateTimeouts:
    """Timeouts auto-transition after a configured dwell period."""

    def test_timeout_fires(self):
        fsm = AgentLifecycleFSMv2(agent_id=30)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.EGG,
                timeout_seconds=0.01,
                target_state=LifecycleState.COMPETE,
            )
        )
        time.sleep(0.02)
        fired = fsm.check_timeouts()
        assert len(fired) == 1
        assert fsm.get_state() == LifecycleState.COMPETE
        assert fired[0].reason == "timeout"

    def test_timeout_does_not_fire_early(self):
        fsm = AgentLifecycleFSMv2(agent_id=31)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.EGG,
                timeout_seconds=10.0,
                target_state=LifecycleState.COMPETE,
            )
        )
        fired = fsm.check_timeouts()
        assert len(fired) == 0
        assert fsm.get_state() == LifecycleState.EGG

    def test_timeout_on_timeout_callback(self):
        called_with: list[int] = []

        def on_timeout(fsm):
            called_with.append(fsm.agent_id)

        fsm = AgentLifecycleFSMv2(agent_id=32)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.EGG,
                timeout_seconds=0.01,
                target_state=LifecycleState.COMPETE,
                on_timeout=on_timeout,
            )
        )
        time.sleep(0.02)
        fsm.check_timeouts()
        assert called_with == [32]

    def test_timeout_updates_state_entered_at(self):
        fsm = AgentLifecycleFSMv2(agent_id=33)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.EGG,
                timeout_seconds=0.01,
                target_state=LifecycleState.COMPETE,
            )
        )
        before = fsm.state_entered_at
        time.sleep(0.02)
        fsm.check_timeouts()
        assert fsm.state_entered_at > before

    def test_clear_timeout(self):
        fsm = AgentLifecycleFSMv2(agent_id=34)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.EGG,
                timeout_seconds=0.01,
                target_state=LifecycleState.COMPETE,
            )
        )
        fsm.clear_timeout(LifecycleState.EGG)
        time.sleep(0.02)
        fired = fsm.check_timeouts()
        assert len(fired) == 0

    def test_timeout_only_for_current_state(self):
        fsm = AgentLifecycleFSMv2(agent_id=35)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.COMPETE,
                timeout_seconds=0.01,
                target_state=LifecycleState.SUNSET,
            )
        )
        time.sleep(0.02)
        # Still in EGG, so COMPETE timeout should not fire
        fired = fsm.check_timeouts()
        assert len(fired) == 0

    def test_is_expired(self):
        fsm = AgentLifecycleFSMv2(agent_id=36)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.EGG,
                timeout_seconds=0.01,
                target_state=LifecycleState.COMPETE,
            )
        )
        assert fsm.is_expired() is False
        time.sleep(0.02)
        assert fsm.is_expired() is True


# ── Auto-Triggers ───────────────────────────────────────────

class TestAutoTriggers:
    """Auto-triggers fire when their condition becomes True."""

    def test_trigger_fires(self):
        fsm = AgentLifecycleFSMv2(agent_id=40)
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=lambda fsm, ctx: True,
                target_state=LifecycleState.COMPETE,
            )
        )
        fired = fsm.check_triggers()
        assert len(fired) == 1
        assert fsm.get_state() == LifecycleState.COMPETE
        assert fired[0].reason == "auto-trigger"

    def test_trigger_does_not_fire_when_false(self):
        fsm = AgentLifecycleFSMv2(agent_id=41)
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=lambda fsm, ctx: False,
                target_state=LifecycleState.COMPETE,
            )
        )
        fired = fsm.check_triggers()
        assert len(fired) == 0
        assert fsm.get_state() == LifecycleState.EGG

    def test_trigger_only_for_current_state(self):
        fsm = AgentLifecycleFSMv2(agent_id=42)
        fsm.transition(LifecycleState.COMPETE)
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=lambda fsm, ctx: True,
                target_state=LifecycleState.COMPETE,
            )
        )
        fired = fsm.check_triggers()
        assert len(fired) == 0

    def test_trigger_on_trigger_callback(self):
        called_with: list[int] = []

        def on_trigger(fsm):
            called_with.append(fsm.agent_id)

        fsm = AgentLifecycleFSMv2(agent_id=43)
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=lambda fsm, ctx: True,
                target_state=LifecycleState.COMPETE,
                on_trigger=on_trigger,
            )
        )
        fsm.check_triggers()
        assert called_with == [43]

    def test_trigger_receives_context(self):
        received: dict[str, object] = {}

        def capture_condition(fsm, ctx):
            received.update(ctx)
            return True

        fsm = AgentLifecycleFSMv2(agent_id=44)
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=capture_condition,
                target_state=LifecycleState.COMPETE,
            )
        )
        fsm.check_triggers(context={"signal": "spawn"})
        assert received.get("signal") == "spawn"

    def test_first_matching_trigger_only(self):
        fsm = AgentLifecycleFSMv2(agent_id=45)
        call_order: list[int] = []

        def t1(fsm, ctx):
            call_order.append(1)
            return True

        def t2(fsm, ctx):
            call_order.append(2)
            return True

        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=t1,
                target_state=LifecycleState.COMPETE,
            )
        )
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=t2,
                target_state=LifecycleState.SUNSET,
            )
        )
        fired = fsm.check_triggers()
        assert len(fired) == 1
        assert fsm.get_state() == LifecycleState.COMPETE
        assert call_order == [1]

    def test_clear_triggers(self):
        fsm = AgentLifecycleFSMv2(agent_id=46)
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=lambda fsm, ctx: True,
                target_state=LifecycleState.COMPETE,
            )
        )
        fsm.clear_triggers()
        fired = fsm.check_triggers()
        assert len(fired) == 0

    def test_trigger_with_guard(self):
        """A trigger's auto-transition is still subject to guards."""
        fsm = AgentLifecycleFSMv2(agent_id=47)
        fsm.register_guard(
            TransitionGuard(
                from_state=LifecycleState.EGG,
                to_state=LifecycleState.COMPETE,
                guard=lambda fsm, ctx: False,
                reason="blocked",
            )
        )
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.EGG,
                condition=lambda fsm, ctx: True,
                target_state=LifecycleState.COMPETE,
            )
        )
        # Trigger fires, but guard blocks it in strict mode
        with pytest.raises(LifecycleTransitionError):
            fsm.check_triggers()


# ── Full Lifecycle Chains ─────────────────────────────────────

class TestFullLifecycleChain:
    """End-to-end with v2 features active."""

    def test_chain_with_timeout(self):
        fsm = AgentLifecycleFSMv2(agent_id=50)
        # COMPETE times out to SUNSET after 1ms (simulating tournament loss)
        fsm.set_timeout(
            StateTimeout(
                state=LifecycleState.COMPETE,
                timeout_seconds=0.01,
                target_state=LifecycleState.SUNSET,
            )
        )
        fsm.transition(LifecycleState.COMPETE, reason="init")
        assert fsm.get_state() == LifecycleState.COMPETE
        time.sleep(0.02)
        fired = fsm.check_timeouts()
        assert len(fired) == 1
        assert fsm.get_state() == LifecycleState.SUNSET

    def test_chain_with_trigger(self):
        fsm = AgentLifecycleFSMv2(agent_id=51)
        # Auto-trigger from SURVIVE to BREED when "selected" in context
        fsm.register_trigger(
            AutoTrigger(
                state=LifecycleState.SURVIVE,
                condition=lambda fsm, ctx: ctx.get("selected") is True,
                target_state=LifecycleState.BREED,
            )
        )
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SURVIVE, reason="win")
        # Not selected yet — trigger doesn't fire
        assert fsm.check_triggers() == []
        assert fsm.get_state() == LifecycleState.SURVIVE
        # Now selected
        fired = fsm.check_triggers(context={"selected": True})
        assert len(fired) == 1
        assert fsm.get_state() == LifecycleState.BREED

    def test_chain_with_guard(self):
        fsm = AgentLifecycleFSMv2(agent_id=52)
        # Only allow BREED if fitness threshold met
        fsm.register_guard(
            TransitionGuard(
                from_state=LifecycleState.SURVIVE,
                to_state=LifecycleState.BREED,
                guard=lambda fsm, ctx: ctx.get("fitness", 0.0) >= 0.8,
                reason="fitness_too_low",
            )
        )
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SURVIVE)
        # Fitness too low
        with pytest.raises(LifecycleTransitionError) as exc:
            fsm.transition(LifecycleState.BREED, context={"fitness": 0.5})
        assert "fitness_too_low" in str(exc.value)
        # Fitness high enough
        fsm.transition(LifecycleState.BREED, context={"fitness": 0.9})
        assert fsm.get_state() == LifecycleState.BREED


# ── History & Introspection ─────────────────────────────────

class TestHistory:
    """Transition history is complete, timestamped, and context-aware."""

    def test_history_includes_init(self):
        fsm = AgentLifecycleFSMv2(agent_id=60)
        hist = fsm.get_history()
        assert len(hist) == 1
        assert hist[0].from_state == LifecycleState.EGG
        assert hist[0].to_state == LifecycleState.EGG
        assert hist[0].reason == "init"

    def test_history_timestamps_monotonic(self):
        fsm = AgentLifecycleFSMv2(agent_id=61)
        time.sleep(0.01)
        fsm.transition(LifecycleState.COMPETE)
        time.sleep(0.01)
        fsm.transition(LifecycleState.SURVIVE)
        hist = fsm.get_history()
        ts = [h.timestamp for h in hist]
        assert ts == sorted(ts)

    def test_history_includes_context(self):
        fsm = AgentLifecycleFSMv2(agent_id=62)
        fsm.transition(LifecycleState.COMPETE, context={"room": 7})
        hist = fsm.get_history()
        assert hist[-1].context.get("room") == 7

    def test_history_copy_is_shallow_safe(self):
        fsm = AgentLifecycleFSMv2(agent_id=63)
        fsm.transition(LifecycleState.COMPETE)
        h1 = fsm.get_history()
        h2 = fsm.get_history()
        assert h1 is not h2
        assert h1 == h2

    def test_last_transition(self):
        fsm = AgentLifecycleFSMv2(agent_id=64)
        fsm.transition(LifecycleState.COMPETE)
        last = fsm.last_transition()
        assert last.to_state == LifecycleState.COMPETE

    def test_idempotent_transition_no_history_dup(self):
        fsm = AgentLifecycleFSMv2(agent_id=65)
        fsm.transition(LifecycleState.COMPETE)
        before = len(fsm.get_history())
        fsm.transition(LifecycleState.COMPETE)
        after = len(fsm.get_history())
        assert before == after

    def test_idempotent_with_reason_appends(self):
        fsm = AgentLifecycleFSMv2(agent_id=66)
        fsm.transition(LifecycleState.COMPETE)
        before = len(fsm.get_history())
        fsm.transition(LifecycleState.COMPETE, reason="heartbeat")
        after = len(fsm.get_history())
        assert after == before + 1


# ── Guard Methods (v1 compat) ──────────────────────────────

class TestGuardMethods:
    """can_breed, can_compete, is_terminal predicates."""

    def test_can_breed_only_survive(self):
        fsm = AgentLifecycleFSMv2(agent_id=70)
        assert fsm.can_breed() is False  # EGG
        fsm.transition(LifecycleState.COMPETE)
        assert fsm.can_breed() is False  # COMPETE
        fsm.transition(LifecycleState.SURVIVE)
        assert fsm.can_breed() is True   # SURVIVE
        fsm.transition(LifecycleState.BREED)
        assert fsm.can_breed() is False  # BREED

    def test_can_compete_egg_and_survive(self):
        fsm = AgentLifecycleFSMv2(agent_id=71)
        assert fsm.can_compete() is True   # EGG
        fsm.transition(LifecycleState.COMPETE)
        assert fsm.can_compete() is False  # COMPETE
        fsm.transition(LifecycleState.SURVIVE)
        assert fsm.can_compete() is True   # SURVIVE
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SUNSET)
        assert fsm.can_compete() is False  # SUNSET

    def test_is_terminal(self):
        fsm = AgentLifecycleFSMv2(agent_id=72)
        assert fsm.is_terminal() is False
        fsm.transition(LifecycleState.COMPETE)
        fsm.transition(LifecycleState.SUNSET)
        fsm.transition(LifecycleState.ARCHIVE)
        assert fsm.is_terminal() is True


# ── Introspection ───────────────────────────────────────────

class TestIntrospection:
    """Registered component snapshots and state metadata."""

    def test_get_registered_guards(self):
        fsm = AgentLifecycleFSMv2(agent_id=80)
        g = TransitionGuard(
            from_state=LifecycleState.EGG,
            to_state=LifecycleState.COMPETE,
            guard=lambda f, c: True,
            reason="test",
        )
        fsm.register_guard(g)
        assert len(fsm.get_registered_guards()) == 1

    def test_get_registered_timeouts(self):
        fsm = AgentLifecycleFSMv2(agent_id=81)
        t = StateTimeout(
            state=LifecycleState.EGG,
            timeout_seconds=1.0,
            target_state=LifecycleState.COMPETE,
        )
        fsm.set_timeout(t)
        assert LifecycleState.EGG in fsm.get_registered_timeouts()

    def test_get_registered_triggers(self):
        fsm = AgentLifecycleFSMv2(agent_id=82)
        tr = AutoTrigger(
            state=LifecycleState.EGG,
            condition=lambda f, c: True,
            target_state=LifecycleState.COMPETE,
        )
        fsm.register_trigger(tr)
        assert len(fsm.get_registered_triggers()) == 1

    def test_time_in_state(self):
        fsm = AgentLifecycleFSMv2(agent_id=83)
        time.sleep(0.01)
        assert fsm.time_in_state() >= 0.01

    def test_state_entered_at_updates_on_transition(self):
        fsm = AgentLifecycleFSMv2(agent_id=84)
        t0 = fsm.state_entered_at
        time.sleep(0.01)
        fsm.transition(LifecycleState.COMPETE)
        t1 = fsm.state_entered_at
        assert t1 > t0


# ── Repr ────────────────────────────────────────────────────

class TestRepr:
    def test_repr(self):
        fsm = AgentLifecycleFSMv2(agent_id=90)
        assert "agent_id=90" in repr(fsm)
        assert "EGG" in repr(fsm)
        assert "AgentLifecycleFSMv2" in repr(fsm)

    def test_repr_after_transition(self):
        fsm = AgentLifecycleFSMv2(agent_id=91)
        fsm.transition(LifecycleState.COMPETE)
        assert "COMPETE" in repr(fsm)
