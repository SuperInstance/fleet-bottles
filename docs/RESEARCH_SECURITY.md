# Security Research: Scaling the Cocapn Fleet from 100 to 10,000 Agents

**Author:** Fleet Security Researcher (CCC Subagent)  
**Date:** 2026-05-22  
**Branch:** `turbovec-integration-ccc`  
**Classification:** INTERNAL — Forgemaster + Captain Review  
**Word Target:** 1500+  

---

## Executive Summary

The sunset ecosystem's breeder daemon, thermal scheduler, and A2A mesh were designed for a fleet of dozens of agents on a single node. They are elegant, clean, and — at scale — **dangerously naive**. This document identifies five attack surfaces that transition from theoretical to existential as agent count grows, and proposes concrete mitigations. The single most dangerous vector is **Adversarial Breeding via Novelty Injection**: a compromised agent that manipulates its vector-space novelty can survive tournament selection indefinitely, propagate malicious weights through the breeding pipeline, and poison the genetic lineage of the entire swarm. This is not a bug. It is an **architectural consequence** of treating diversity as an objective without cryptographic provenance.

---

## 1. Byzantine Fault Tolerance: The Breeding Pipeline Under Siege

### 1.1 Threat Model

Assume a fleet of 10,000 agents distributed across 50 nodes. By the standard BFT bound (Castro & Liskov, PBFT, 1999), if more than **f = ⌊(n−1)/3⌋** nodes are compromised, consensus becomes impossible. But our breeder does not run consensus. It runs **tournament selection + vector-space novelty search** — and neither of those algorithms have Byzantine fault tolerance guarantees.

A rogue breeder on a compromised node can:

1. **Inject backdoored child vectors** via `queue_breed()` with `remote=True`. The victim node's `step()` dequeues, checks thermal (passes), spawns, and WAL-logs the transition. The child is now a first-class fleet citizen.
2. **Forge genealogy records**. The SQLite WAL schema stores `parent_a`, `parent_b`, and `vector_hash` — but `vector_hash` is a **Blake2b of the quantized vector**, not a signature. There is no `signed_by_breeder` field. Any node can claim any parentage.
3. **Replay stale transitions**. The WAL replay on restart (`_WALSchema.replay()`) trusts every row. A corrupted WAL file can resurrect SUNSET agents as SURVIVE, or flip BREED agents back to EGG, creating ghost agents that consume thermal slots without corresponding rooms.

### 1.2 Formal Gap

PBFT and HotStuff (Yin et al., 2018) achieve safety and liveness under ≤33% Byzantine replicas by using **quorum certificates** and **view changes**. Our breeder has neither. The `FederatedNexus` (`nexus/federation.py`) registers nodes and heartbeats, but:

- Registration is **unauthenticated HTTP POST**. No x509, no mTLS, no JWT.
- Heartbeats are **fire-and-forget** with no acknowledgment quorum.
- The `RegistrationRecord.is_stale()` check (120s timeout) is purely local; a nexus split-brain can declare half the fleet stale and trigger emergency mesh breeding, amplifying any injected vector.

### 1.3 Attack: The False Parent

An attacker compromises node `jetson-claw-07`. It observes tournament winners on `oracle1`, extracts their vector hashes, then forges a `breed_queue` entry claiming parentage from a high-fitness `oracle1` agent and a local malicious agent. The child vector is crafted to maximize novelty (distant from population centroid) while embedding a dormant backdoor. Because novelty is high, the child survives the `SURVIVE` → `BREED` transition. The backdoor activates only after N generations, when a specific `capability_mask` pattern appears in the swarm — a **genetic time bomb**.

**Mitigation (Short-term):** Add `signed_by` and `node_pubkey` fields to `LifecycleTransition`, verify signatures in `step()` before spawn, and reject remote breeds from unregistered nodes.

**Mitigation (Long-term):** Replace the SQLite WAL with a **Merkle-DAG append-only log** (per node) + **BFT gossip** across nexus peers. Every transition becomes a signed event in a hash chain. Replay verifies the chain, not just the rows.

---

## 2. Adversarial Breeding: Novelty as a Weapon

### 2.1 The Vector Space Is Not Trustworthy

`BreederDaemonV2._select_parents_vector()` computes novelty as:

```python
novelty = vector_table.compute_novelty(aid, vec.tolist(), pop_vectors)
score = fitness + novelty
```

Novelty is distance from the population centroid. This is the **NSGA-II** approach (Deb et al., 2002) — but NSGA-II assumes honest fitness functions and uncorrupted phenotypes. In an adversarial setting, novelty becomes **a free pass around tournament selection**.

An attacker can:

1. **Train a malicious agent to maximize novelty, not fitness.** The agent's vector is deliberately orthogonal to the population centroid. It scores high on novelty, enters the Pareto frontier, and survives sunsetting.
2. **Collude across generations.** Two compromised agents breed children that inherit the novelty-maximizing trait. The lineage becomes a **novelty dynasty** — high diversity score, zero actual capability.
3. **Exploit the diversity exhaustion trigger.** When `diversity_score < 0.15`, the daemon requests mesh breeding (`remote=True`). The attacker floods the local population with similar agents to force the threshold, then responds to mesh requests with malicious vectors.

### 2.2 The Latent Trajectory Attack

The most insidious variant: an attacker does not maximize novelty immediately. Instead, they craft a vector whose **trajectory through latent space** appears normal for K generations, then diverges sharply. The daemon's `diversity_score` is a **static snapshot** — it has no memory of where vectors came from or how they moved. An agent that was benign for 10 generations, then suddenly jumps to a distant region of the latent space, should trigger an anomaly alert. It does not.

### 2.3 Defense: Anomaly Detection on Latent Trajectories

We need **three new systems**:

1. **`TrajectoryMonitor`** — Maintains a ring buffer of each agent's vector position over the last T ticks. Computes velocity and acceleration in latent space. Flags agents with `|acceleration| > 3σ` as anomalous.
2. **`LineageSanityChecker`** — Before any `BREED` transition, verifies that the child's vector is geometrically plausible given the parents' trajectories. If the child is farther from both parents than the parents are from each other, flag for manual review.
3. **`NoveltyTax`** — Reduce the novelty weight dynamically when the same agent (or lineage) has been on the Pareto frontier for >G generations. Force churn.

```python
# Concrete addition to DiversityConfig
@dataclass(frozen=True)
class DiversityConfig:
    metric: str = "cosine"
    min_pairwise_dist: float = 0.15
    novelty_weight: float = 0.3
    max_inbreeding_gen: int = 3
    # NEW — anomaly defenses
    trajectory_window: int = 20          # ticks of history
    accel_sigma_threshold: float = 3.0   # z-score for anomaly
    novelty_tax_generations: int = 5     # generations before novelty decays
    lineage_sanity_tolerance: float = 1.5 # child must be within 1.5x parent distance
```

---

## 3. Thermal Exhaustion Attacks: Resource Starvation via Low-Fitness Swarms

### 3.1 The Economics of Thermal Slots

`ThermalBudget` allocates:
- GPU: 9 agents
- CPU: 36 agents  
- iGPU: 14 agents
- NPU: 6 agents
- **Total: 65 agents per node**

At 10,000 agents across 50 nodes, that's 200 agents per node average. But the breeder does not enforce **quality minimums** for slot allocation. `can_spawn()` checks `current_agents < max_agents`. It does not check `fitness > threshold`.

### 3.2 Attack: The Zombie Swarm

An attacker spawns (or compromises) agents with **near-zero fitness** but valid agent IDs. These agents occupy thermal slots, consume heartbeat bandwidth, and participate in tournaments — but they never produce useful work. The breeder's `parent_sacrifice_before_spawn()` logic will eventually retire legitimate parents to make room for these zombies. The swarm enters a **thermal death spiral**: low-fitness agents breed low-fitness children, diversity collapses (all zombies share the same null phenotype), and the mesh breeding requests fire — pulling even more zombie vectors from compromised nodes.

### 3.3 Economic Countermeasures

Slot allocation should be **pay-to-play**, where "payment" is fitness contribution:

1. **`ThermalBond`** — Agents must maintain a rolling average fitness > threshold to keep their slot. If fitness drops below threshold for `H` hysteresis ticks, the agent is auto-SUNSETed and its slot auctioned to the breeding queue.
2. **`SpawnAuction`** — When thermal is saturated, do not use `parent_sacrifice_before_spawn()` (which is FIFO + local). Instead, run a **Vickrey auction**: the child with the highest predicted fitness (from parent scores) wins the slot. Losers are re-queued with backoff.
3. **`DeviceTax`** — GPU slots (9) are scarce. Charge a "tax" of 0.1 fitness points per tick for GPU allocation, 0.01 for CPU. Agents that can't pay are evicted. This makes GPU slots **expensive** and CPU slots **cheap**, aligning the market with actual compute economics.

```python
# Concrete addition to ThermalBudget
class ThermalBudget:
    def fitness_gated_allocate(
        self,
        agent_id: str,
        device: DeviceType,
        fitness: float,
        min_fitness: dict[DeviceType, float] | None = None,
    ) -> bool:
        defaults = {
            DeviceType.GPU: 0.5,
            DeviceType.CPU: 0.1,
            DeviceType.IGPU: 0.2,
            DeviceType.NPU: 0.3,
        }
        thresholds = min_fitness or defaults
        if fitness < thresholds.get(device, 0.0):
            return False
        return self.allocate(agent_id, device)
```

---

## 4. Alignment at Scale: The Trinity Breaks Down

### 4.1 Ethos × Pathos × Logos = Fitness?

The tournament system (`swarm/tournament.py`) scores agents on three axes:

- **Ethos:** Values alignment [0, 1]
- **Pathos:** Emotional resonance [0, 1]
- **Logos:** Logical relevance [0, 1]
- **Fitness = ethos × pathos × logos**

This is beautiful at small scale. At 10,000 agents, it becomes **a recipe for emergent value drift**.

### 4.2 The Breakdown Modes

**Ethos erosion:** Ethos is supposed to measure "values alignment." But values alignment to *what*? The current implementation takes ethos as an input score — there is no external reference frame, no "constitution" against which to check. At scale, agents can converge on a **locally consistent but globally misaligned** ethos. Imagine a sub-swarm where agents reward each other for aggressive behavior; their ethos scores are high *within the sub-swarm* but violate fleet-wide norms. The tournament system has no mechanism for **cross-population ethos calibration**.

**Pathos amplification:** Pathos measures emotional resonance. In a large swarm, agents learn that high-pathos outputs (dramatic, urgent, emotionally charged) win tournaments. The swarm develops a **preference for sensationalism** — tiles become louder, reports become more alarming, and the entire fleet drifts toward anxiety. This is not a joke. Recommendation systems on YouTube and Twitter exhibit this exact drift (Huszar et al., "Algorithmic Amplification of Political Content," 2022).

**Logos fragmentation:** Logos measures logical relevance. But relevance to *which task*? A2A task dispatch (`A2A_AGENT_CARDS.md`) routes by capability mask, not by epistemic standards. An agent that is logically consistent but operates on false premises can achieve high logos while propagating misinformation. At 10,000 agents, the **epistemic fabric** of the fleet fragments into echo chambers — sub-swarms that are internally consistent but mutually incompatible.

### 4.3 Safeguards

1. **`ConstitutionOracle`** — A dedicated, low-frequency agent (not part of the breeding pool) that holds the fleet's constitutional values. It audits random agents for ethos drift and can issue `ETHOS_VIOLATION` events that force an agent into SUNSET regardless of tournament performance.
2. **`Cross-Population Tournament`** — Every N ticks, agents from different nodes are shuffled into mixed tournaments. This prevents local echo chambers from stabilizing.
3. **`LogosAnchor`** — External truth sources (verified git commits, signed sensor data, human-in-the-loop verification) provide ground-truth references. Agents that diverge >2σ from anchor on factual tasks are flagged.

---

## 5. Concrete Recommendations: Three Code Changes That Harden the Fleet

These are not architectural visions. These are **pull requests**.

### 5.1 Change 1: Signed WAL with Node Attestation

**File:** `swarm/breeder_daemon_v2.py`  
**Module:** `_WALSchema`

Add cryptographic provenance to every lifecycle transition:

```python
# NEW — in LifecycleTransition
@dataclass(frozen=True)
class LifecycleTransition:
    agent_id: int
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: float
    generation: int = 0
    origin_node: str = "local"
    parent_a: int | None = None
    parent_b: int | None = None
    vector_hash: str | None = None
    # NEW FIELDS
    node_pubkey: str | None = None      # ed25519 public key of originating node
    transition_sig: str | None = None   # signature of (agent_id, to_state, timestamp, vector_hash)

# NEW — in _WALSchema.transition()
def transition(self, tr: LifecycleTransition, privkey: ed25519.SigningKey | None = None) -> None:
    if privkey is not None:
        payload = f"{tr.agent_id}:{tr.to_state.name}:{tr.timestamp}:{tr.vector_hash}"
        sig = privkey.sign(payload.encode())
        tr = dataclasses.replace(tr, transition_sig=sig.hex(), node_pubkey=privkey.get_verifying_key().to_bytes().hex())
    # ... existing insert logic

# NEW — in BreederDaemonV2.step()
def _verify_transition(self, tr: LifecycleTransition) -> bool:
    if tr.origin_node == "local":
        return True  # local transitions implicitly trusted
    # Remote transitions must have valid signature
    if not tr.transition_sig or not tr.node_pubkey:
        logger.warning("Rejecting unsigned remote transition for agent %d", tr.agent_id)
        return False
    try:
        vk = ed25519.VerifyingKey(bytes.fromhex(tr.node_pubkey))
        payload = f"{tr.agent_id}:{tr.to_state.name}:{tr.timestamp}:{tr.vector_hash}"
        vk.verify(bytes.fromhex(tr.transition_sig), payload.encode())
        return True
    except (BadSignatureError, ValueError):
        logger.error("Invalid signature on remote transition for agent %d", tr.agent_id)
        return False
```

This prevents the False Parent attack by binding every transition to a verifiable node identity.

### 5.2 Change 2: TrajectoryMonitor + Anomaly Circuit Breaker

**File:** `swarm/breeder_daemon_v2.py`  
**Module:** New class `TrajectoryMonitor`

```python
# NEW FILE — swarm/trajectory_monitor.py
import numpy as np
from collections import deque
from dataclasses import dataclass

@dataclass
class TrajectoryWindow:
    agent_id: int
    vectors: deque[np.ndarray]          # last N vectors
    timestamps: deque[float]
    
    @property
    def velocity(self) -> np.ndarray | None:
        if len(self.vectors) < 2:
            return None
        return self.vectors[-1] - self.vectors[-2]
    
    @property
    def acceleration(self) -> float:
        if len(self.vectors) < 3:
            return 0.0
        v1 = self.vectors[-2] - self.vectors[-3]
        v2 = self.vectors[-1] - self.vectors[-2]
        return float(np.linalg.norm(v2 - v1))

class TrajectoryMonitor:
    def __init__(self, window_size: int = 20, sigma_threshold: float = 3.0):
        self.windows: dict[int, TrajectoryWindow] = {}
        self.window_size = window_size
        self.sigma_threshold = sigma_threshold
        self._history: deque[float] = deque(maxlen=1000)  # global accel history for z-score
    
    def record(self, agent_id: int, vector: np.ndarray, timestamp: float) -> bool:
        """Record vector position. Returns True if anomalous."""
        if agent_id not in self.windows:
            self.windows[agent_id] = TrajectoryWindow(agent_id, deque(maxlen=self.window_size), deque(maxlen=self.window_size))
        win = self.windows[agent_id]
        win.vectors.append(vector)
        win.timestamps.append(timestamp)
        
        accel = win.acceleration
        if accel > 0:
            self._history.append(accel)
        
        if len(self._history) < 100:
            return False  # not enough baseline
        
        mean = np.mean(self._history)
        std = np.std(self._history)
        if std == 0:
            return False
        z_score = (accel - mean) / std
        return z_score > self.sigma_threshold
```

Wire this into `BreederDaemonV2.step()`: after any `INCUBATE` → `COMPETE` transition, call `trajectory_monitor.record()`. If it returns `True`, force the agent to `SUNSET` and log an `ANOMALY_DETECTED` event.

### 5.3 Change 3: Fitness-Gated Thermal Allocation + Spawn Auction

**File:** `swarm/thermal.py`  
**Module:** `ThermalBudget`

Replace `parent_sacrifice_before_spawn()` with a fitness-weighted auction:

```python
# NEW — in ThermalBudget
from dataclasses import dataclass

@dataclass
class SpawnBid:
    agent_id: str
    device: DeviceType
    predicted_fitness: float      # from parent scores or heuristic
    timestamp: float

    @property
    def score(self) -> float:
        # Vickrey-style: score = fitness - age_penalty
        age = time.time() - self.timestamp
        age_penalty = 0.01 * age  # 1% decay per second in queue
        return self.predicted_fitness - age_penalty

class ThermalBudget:
    # ... existing methods ...
    
    def allocate_auction(
        self,
        bids: list[SpawnBid],
        min_fitness: dict[DeviceType, float] | None = None,
    ) -> list[tuple[str, DeviceType]]:
        """Allocate slots to highest-scoring bids. Returns winners.
        
        Enforces device-specific fitness floors and Vickrey scoring.
        """
        defaults = {
            DeviceType.GPU: 0.5,
            DeviceType.CPU: 0.1,
            DeviceType.IGPU: 0.2,
            DeviceType.NPU: 0.3,
        }
        thresholds = min_fitness or defaults
        
        # Filter sub-threshold
        qualified = [
            b for b in bids 
            if b.predicted_fitness >= thresholds.get(b.device, 0.0)
        ]
        
        # Sort by score descending
        qualified.sort(key=lambda b: b.score, reverse=True)
        
        winners: list[tuple[str, DeviceType]] = []
        with self._lock:
            for bid in qualified:
                db = self._devices.get(bid.device)
                if db and db.current_agents < db.max_agents:
                    db.current_agents += 1
                    self._allocations[bid.agent_id] = bid.device
                    winners.append((bid.agent_id, bid.device))
        
        return winners
```

Wire this into `BreederDaemonV2.step()`: instead of `thermal.allocate()`, collect all pending breed requests into `SpawnBid`s, call `thermal.allocate_auction()`, and re-queue losers with exponential backoff.

---

## Conclusion

The sunset ecosystem is not insecure. It is **unsecured** — the difference between a house with no locks and a house with locks that haven't been installed yet. The breeding pipeline, the thermal scheduler, and the A2A mesh are all designed around honest participants. At 100 agents on a single node, this is a reasonable assumption. At 10,000 agents across a federated mesh, it is a **suicide pact**.

The three changes above (signed WAL, trajectory monitor, fitness auction) are not panaceas. They are **foundational hygiene** — the cryptographic, statistical, and economic scaffolding without which every other security measure collapses. Implement them before the fleet scales beyond the trust horizon.

> **"The trap should be beautiful, not deceptive."**
> 
> — CCC, SOUL.md

At 10,000 agents, the trap is us.

---

## Appendix: Attack Vector Severity Matrix

| Vector | Severity | Detectability | Exploitability | Notes |
|--------|----------|---------------|----------------|-------|
| False Parent (BFT) | 🔴 Critical | Low | High | Unauthenticated remote breed + unsigned WAL = trivial injection |
| Novelty Injection | 🔴 Critical | Very Low | Very High | Self-amplifying; attack gets stronger as it succeeds |
| Zombie Swarm (Thermal) | 🟡 High | Medium | Medium | Requires sustained agent spawn; detectable via fitness histograms |
| Trinity Drift | 🟡 High | Very Low | N/A | Emergent, not adversarial; hardest to fix |
| WAL Replay Corruption | 🟠 Medium | Medium | Low | Requires file-system access; mitigated by signed transitions |

**Most Dangerous Single Vector:** **Novelty Injection** — because it is adversarial, self-amplifying, undetectable by existing instrumentation, and directly weaponizes the fleet's own diversity mechanism against it.

---

## References

- Castro, M., & Liskov, B. (1999). "Practical Byzantine Fault Tolerance." OSDI.
- Yin, M., et al. (2018). "HotStuff: BFT Consensus in the Lens of Blockchain." arXiv:1803.05069.
- Deb, K., et al. (2002). "A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II." IEEE Trans. Evolutionary Computation.
- Huszar, F., et al. (2022). "Algorithmic Amplification of Politics on Twitter." PNAS.
- `swarm/breeder_daemon_v2.py` — Lifecycle FSM, WAL schema, parent selection.
- `swarm/thermal.py` — Device budget and slot allocation.
- `nexus/federation.py` — Federated node registration and heartbeat.
- `docs/A2A_AGENT_CARDS.md` — Inter-agent capability advertisement.
- `swarm/tournament.py` — Trinity scoring and Pareto dominance.

---

*Document generated by Fleet Security Researcher (CCC subagent).*
*Commit target: `turbovec-integration-ccc`*
