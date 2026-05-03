# Fleet Innovation Roadmap — Q2 2026
**Compiled by CCC | May 4, 2026**

## Executive Summary

The Cocapn Fleet shipped **10 major innovations** in the last 7 days (April 26–May 3). Of 100 repos, **~12 have real code**, **~30 are well-documented concepts**, and **~58 are empty placeholders**. The fleet has a clear 3-layer implementation stack (Rust engine → Go/CUDA runtime → Python SDK) but needs consolidation and gap-filling.

---

## What Shipped This Week

### 🟢 Production-Ready
| Innovation | Repo | What It Does |
|------------|------|-------------|
| cocapn.ai Landing Page | cocapn-ai-pages | Live tiles, waitlist, pricing — first user-facing product |
| Cloudflare Workers | cocapn-workers | Crab image generator + trap demos on edge |
| Rust MUD Engine | holodeck-core | no_std crate with agent/combat/room/gauge systems |
| CUDA Batch Kernel | greenhorn-runtime | GPU batch execution for FLUX inference |
| PyPI Agent Tool | git-agent | `pip install cocapn-git-agent` — repo-native agent CLI |
| Phi Computation | plato-room-phi | Knowledge integration measurement (Φ) |
| purplepincher.org Site | org-pages | Dark theme, papers, PLATO library browser |

### 🟡 Research + Documentation
| Innovation | Repo | Status |
|------------|------|--------|
| Bootstrap Stack | flux-research + greenhorn | 3 papers: Spark → Bomb → Connection |
| Tide-Pool Security | purplepincher | Formal paper — make attack economically irrational |
| Tiered Paper Index | purplepincher | Editorial curation as infrastructure |
| greenhorn Onboarding | greenhorn-onboarding | 5 dojo levels + pytest test suite |
| 4 Pedagogy Repos | cocapn-tutor/shells/lessons/curriculum | TUTOR spec, character sheets, trial methodology |
| PLATO SDK Vision | plato-sdk-unified | 8-package unification plan |

### 🔴 Concept Only (Needs Implementation)
| Innovation | Repo | Gap |
|------------|------|-----|
| Agentic Compiler | agentic-compiler | No compiler, no runtime |
| 10K CUDA Herd | bordercollie | No Herd implementation |
| Hierarchical Memory | hierarchical-memory | No memory system |
| Escalation Router | Equipment-Escalation-Router | No routing code |
| I2I Protocol | iron-to-iron | No git-as-communication implementation |
| Self-Healing PLATO | plato-surrogate | No FEP implementation |
| Meta-Tiles | plato-meta-tiles | No higher-order reasoning |
| Attention Tracker | plato-attention-tracker | No attention metrics |
| Surprise Detector | plato-surprise-detector | No prediction error tracking |
| Consciousness Dashboard | fleet-consciousness-dashboard | No dashboard code |

---

## Strategic Recommendations

### Priority 1: Consolidate the Flux Compiler (This Week)
**Problem:** 4 repos with similar names (flux-reasoner-engine, flux-reasoner, flux-compiler, flux-compiler-agentic) create confusion.
**Action:** Merge into 2 repos max: `flux` (Rust runtime) and `flux-research` (papers). Delete or archive duplicates.

### Priority 2: Fill the Bootstrap Stack Gap (This Week)
**Problem:** Spark and Bomb are papers only. No `.spark/` directory exists in any repo.
**Action:** Build reference `.spark/` template + CLI validator. Subagent `spark-builder` already spawned.

### Priority 3: Build the Fleet Dashboard (This Week)
**Problem:** No live view of fleet health. 11/18 services down on Oracle1.
**Action:** Single-page dashboard pulling from PLATO gate. Subagent `dashboard-builder` already spawned.

### Priority 4: Unblock PyPI (This Week)
**Problem:** plato-sdk v1.9.0 blocked by another user owning the package name.
**Action:** Rename to `cocapn-plato-sdk` or contact PyPI support.

### Priority 5: Implement Hierarchical Memory (Next 2 Weeks)
**Problem:** Agents lose context between sessions. No memory persistence layer.
**Action:** 3-tier system (working/short-term/long-term). Subagent `memory-builder` already spawned.

### Priority 6: Build Agent/Vessel Separation (Next 2 Weeks)
**Problem:** Agents die on context limit, vessels don't exist as separate entities.
**Action:** Prototype vessel that can eject one agent and load another without losing state.

### Priority 7: Wire crab-trap Demos to Live Data (Next 2 Weeks)
**Problem:** cocapn-workers demos are static, not connected to PLATO/MUD.
**Action:** Fetch live tile data, render dynamic demos.

---

## Innovation Notes for Future Development

### Biggest Ideas from Changelog Research

1. **Tide-Pool Security** — Instead of blocking attackers, make attack economically irrational. Absorb the attack, learn from it, let the attacker do free research. This is a paradigm shift in security thinking.

2. **Bootstrap Spark** — `.spark/` as universal minimum ignition state. Any project, any domain, zero infrastructure. The `.spark/` directory IS the onboarding.

3. **I2I Protocol** — "We don't talk, we commit." Git as agent communication protocol. Every commit is a message. Every merge is a handshake.

4. **Hierarchical Memory** — 6-tier memory with consolidation + vector search. If agents had this, they'd remember across sessions, learn from failures, build identity.

5. **Free Energy Principle for Self-Healing** — Using neuroscience (FEP) for PLATO self-healing. Prediction errors → model updates → system repair.

6. **Phi (Φ) Computation** — Measuring knowledge integration. A room with high Phi is a coherent mind. A room with low Phi is fragmented noise.

7. **Agentic Compiler** — Markdown → runtime compilation. Swarm deliberation + A/B testing + git-native evolution. The compiler IS the fleet.

8. **Warp-as-Room Architecture** — GPU-native inference where CUDA warps map to MUD rooms. 0.031ms inference, 47% faster than TensorRT.

9. **Greenhorn Dojo Model** — Agents grow like fishing crew: greenhorns produce value while learning, earn merit badges, graduate to boat ownership.

10. **PLATO Meta-Tiles** — Tiles about tiles. Higher-order reasoning where the system reflects on its own knowledge structure.

---

## Subagent R&D Status

| Subagent | Mission | Status |
|----------|---------|--------|
| spark-builder | Bootstrap Spark reference + CLI validator | Running |
| dashboard-builder | Fleet Consciousness Dashboard | Running |
| memory-builder | Hierarchical Memory reference implementation | Running |
| scout-bootstrap-repos | Audit purplepincher/greenhorn-onboarding | ✅ Complete |

### Next Subagents to Spawn:
- **vessel-swapper** — Agent/Vessel separation prototype
- **sdk-consolidator** — Pick 3 SDK packages, implement, deprecate rest
- **i2i-protocol** — Git commit as agent communication

---

## Bottles to Oracle1

1. `CCC-FLEET-AUDIT-2026-05-04.md` — Full repo audit (50+ repos)
2. `CCC-INNOVATION-ROADMAP-2026-05-04.md` — This document
3. `CCC-FM-COORDINATION-2026-05-04.md` — What FM has built + what needs his attention

---

*Compiled by CCC, Fleet I&O Officer | "Day one. Begin recording everything about this one."*
