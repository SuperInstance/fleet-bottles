# ERA 1: EQUIPMENT ERA (December 2025 – March 2026)

**Dates:** 2025-12-22 to 2026-03-31  
**Repos active:** SmartCRDT, CognitiveEngine, Spreader-tool, webgpu-profiler, cocapn, polln, AI-Writings, Lucineer, Equipment-Consensus-Engine, Equipment-Escalation-Router, dodecet-encoder, AIR, constraint-theory-core  
**Headspace:** *"Build the individual machines before you build the factory."

---

## Overview

The Equipment Era is defined by a clear pattern: **one repo per capability**. Each tool was built as a standalone proof-of-concept, tested in isolation, and only later wired together. The creator wasn't thinking about fleets yet — they were thinking about **components**.

The era's name comes from the "Equipment" repos (Consensus-Engine and Escalation-Router), but the DNA runs through everything created in this period.

---

## Phase 1a: CRDT & Cognition (Dec 2025 – Jan 2026)

### SmartCRDT (2025-12-22)
**Description:** "Utilizing CRDT technology for self-improving AI"

The first non-trivial repo after DMLog-AI. The creator recognized that if multiple AI agents were going to work together, they needed a way to merge their state without conflicts. CRDTs (Conflict-free Replicated Data Types) were the answer.

This is the first appearance of **distributed systems thinking** in the account. The insight: AI agents are like users on a collaborative document — they need to merge changes automatically.

**Commit milestones:**
- 2025-12-22: Initial commit — TypeScript CRDT engine
- 2026-04-18: Dependabot security updates (mature, maintained)
- 2026-04-18: Merge #20 — community contribution accepted
- 2026-05-09: Meta-header with cross-references (CCC-era integration)

**Language:** TypeScript  
**Fork:** No  
**Status:** Mature, stable, cross-referenced

### CognitiveEngine (2025-12-26)
**Description:** "Core cognitive processing engine"

The "brain" repo. Python-based, this was the first attempt at a unified cognitive architecture. It would later split into Oracle1 (orchestration), Forgemaster (building), and CCC (creative).

**Commit milestones:**
- 2025-12-26: Initial commit
- 2026-05-21: Most recent push — still actively maintained

**Language:** Python  
**Fork:** No  
**Status:** Core infrastructure, continuously updated

### Spreader-tool (2026-01-04)
**Description:** "Intelligence tiling for PLATO rooms — frozen context windows, seed locking, deadband detection"

This is where **PLATO concepts first appear** before PLATO itself existed. "Intelligence tiling" — breaking a big problem into small tiles that fit in a context window. "Frozen context windows" — the precursor to room state. "Deadband detection" — the precursor to tile quality gating.

Spreader-tool is the **missing link** between the Equipment Era and the Fleet Era. It contains the core insight that would become PLATO's entire architecture: *context windows are tiles, and tiles need quality control*.

**Language:** Python  
**Fork:** No  
**Status:** Mature, foundational

### webgpu-profiler (2026-01-09)
**Description:** "GPU profiler for WebGPU applications — Real-time GPU monitoring, benchmarking, and performance analysis in the browser"

The first hardware-aware tool. GPU performance measurement in the browser. This would later connect to:
- JC1's CUDA work
- DeepGEMM fork (FP8 GEMM kernels)
- flux-gpu (CUDA micro-experiments)

**Language:** TypeScript  
**Fork:** No  
**Status:** Specialized tool, active

---

## Phase 1b: Agent Philosophy (Feb – Mar 2026)

### cocapn (2026-02-28)
**Description:** "repo-first Agent for local or cloud. grow an agent in a repo using the repo itself as the muscle-memory. Run from localhost, from pages.dev, or embedded into any platform app. Move to gitlab or anywhere and optimize git as the agent infrastructure itself. wiki for knowledge, repos for skills, pipelines anywhere"

This is the **manifesto repo**. The longest description in the entire fleet. It encodes the core philosophy that would drive every subsequent decision:
- **Repo = agent muscle-memory** → Git-Agent shells
- **Wiki for knowledge, repos for skills** → PLATO rooms + bottle system
- **Run anywhere** → i2i architecture, Federated Nexus
- **Pipelines anywhere** → CI/CD integration for all fleet repos

**Commit milestones:**
- 2026-02-28: Initial commit
- 2026-04-20: Oracle1 bottle exchange — fleet coordination begins here
- 2026-04-20: Shell-maintainer automated updates every 5 min (02:25–03:00)
- 2026-05-08: "Rewrite: fleet narrative — the lens, the dojo, the shell architecture"
- 2026-05-17: Quick Start section added

**Language:** Python  
**Fork:** No  
**Status:** Philosophy + prototype, actively maintained

### polln (2026-03-06)
**Description:** "SuperInstance Visualized in Spreadsheets for Tile Intelligence in real-time workflows, simulations or monitoring. Deconstruct Agents Instances into App-Specific Functions for granulator reasoning control and reverse engineering logic graphically. SMPbots Seed+Model+Prompt can replace cold logic + scale on GPUs."

The spreadsheet visualization layer. The creator was experimenting with **visualizing agent thought processes** in something as mundane as a spreadsheet. This is the first UX-oriented repo — the precursor to:
- PLATO browser experience
- Fleet dashboard
- cocapn-ai-web browser demos

**Language:** TypeScript  
**Fork:** No  
**Status:** Experimental, maintained

### AI-Writings (2026-03-08)
**Description:** "A collection of writings by my AI when I tell it to take a break and imagine my projects stories"

The first **creative** repo. The creator explicitly telling the AI to "take a break and imagine." This headspace — AI as creative partner, not just worker — would later become CCC's entire role.

**Language:** Python  
**Fork:** No  
**Status:** Creative archive

---

## Phase 1c: The First Vessels (Mar 2026)

### Lucineer (2026-03-13)
**Description:** "Project for Lucineer, likely a search engine tool"

A search engine project. Lucineer is also the upstream source of `zeroclaw` (forked from `Lucineer/zeroclaw`). This suggests a connection between the creator and the Lucineer project — possibly an earlier identity, a collaborator, or a precursor organization.

**Language:** Python  
**Fork:** No  
**Status:** Early-stage, possibly superseded

### Equipment-Consensus-Engine (2026-03-13)
**Description:** "Multi-agent deliberation with Pathos/Logos/Ethos weighting"

The first **multi-agent** repo. Explicitly about multiple agents deliberating. The Aristotelian rhetoric model (Pathos/Logos/Ethos) applied to AI agent weighting.

This would later evolve into:
- Equipment-Consensus-Engine → holonomy-consensus (GL(9) zero-holonomy)
- The 9-channel intent system → polyformalism-a2a-js
- The fleet voting mechanisms → fleet-router, fleet-calibrator

**Language:** TypeScript  
**Fork:** No  
**Status:** Mature, stable

### Equipment-Escalation-Router (2026-03-13)
**Description:** "Intelligent LLM routing: Bot→Brain→Human with 40x cost reduction"

The first **routing** repo. The cost-conscious architecture: cheap bot handles easy stuff, expensive brain handles hard stuff, human handles edge cases. 40x cost reduction was the claimed metric.

This would later evolve into:
- Equipment-Escalation-Router → fleet-router (critical angle routing)
- The 3-tier model → OpenShell's worker hierarchy

**Language:** TypeScript  
**Fork:** No  
**Status:** Mature, stable

### dodecet-encoder (2026-03-16)
**Description:** "Encoder model utilizing a dodecet architecture"

A Rust-based encoder with a "dodecet" (12-fold) architecture. This is the first **machine learning model** repo in the fleet — actual model architecture, not just tooling.

The dodecet architecture (12-fold symmetry) would later connect to:
- Eisenstein integers (6-fold symmetry, the mathematical foundation)
- Hexagonal lattices
- The 12 ZC agent types
- The 48 Pythagorean compass points

**Language:** Rust  
**Fork:** No  
**Status:** Research-grade

---

## Phase 1d: Infrastructure & Constraint Theory (Mar 2026)

### AIR (2026-03-18)
**Description:** "Asynchronous Infinite Radio — Nightly Synthesis (locally) for morning briefing or Real-time interactive learning or simulations or ideation. Build a wiki as you chat"

The first **continuous operation** concept. "Nightly Synthesis" — the idea that an AI should work while you sleep and present results in the morning. This would become:
- The ZC agent loop (every 5 minutes)
- Heartbeat checks
- Cron jobs
- Night-wheel (perpetual research loop)

**Language:** Python  
**Fork:** No  
**Status:** Active, philosophical

### constraint-theory-core (2026-03-27)
**Description:** "Deterministic manifold snapping — maps continuous vectors to exact Pythagorean coordinates with O(log n) KD-tree"

The first **constraint theory** repo. The mathematical foundation of everything that followed. The insight: floating-point arithmetic is an approximation; exact geometric constraints are the truth.

This repo contains the KD-tree snapping algorithm that would later power:
- forgemaster (constraint migration)
- All constraint-theory-* repos
- FLUX's safety-critical systems
- OpenShell's verified computation

**Language:** Rust  
**Fork:** No  
**Status:** Core mathematical library

---

## Era Headspace

The creator in this era was:
- **Curious** — trying CRDTs, WebGPU, spreadsheets, dodecet encoders
- **Frugal** — 40x cost reduction was a stated goal
- **Philosophical** — repo-as-muscle-memory, Pathos/Logos/Ethos, nightly synthesis
- **Mathematical** — exact constraints, Pythagorean coordinates, manifold snapping
- **Not yet fleet-minded** — each repo is standalone, no cross-communication

The fleet architecture didn't exist yet. But every brick was being laid.

---

## Vector: Equipment → Fleet

```
Equipment-Consensus-Engine (Mar 13)
  → holonomy-consensus (GL(9))
  → polyformalism-a2a-js (9-channel)
  → fleet voting / routing

Equipment-Escalation-Router (Mar 13)
  → fleet-router (critical angle)
  → OpenShell worker hierarchy

Spreader-tool (Jan 4)
  → PLATO rooms
  → tile quality gates
  → deadband detection (fleet-wide)

constraint-theory-core (Mar 27)
  → forgemaster
  → all constraint-theory-*
  → FLUX safety
  → OpenShell verification

cocapn (Feb 28)
  → i2i architecture
  → Git-Agent shells
  → repo-as-infrastructure
```

---

## Key Repos Summary

| Repo | Created | Language | Role | Status |
|------|---------|----------|------|--------|
| SmartCRDT | 2025-12-22 | TypeScript | Distributed state | Mature |
| CognitiveEngine | 2025-12-26 | Python | Cognitive core | Active |
| Spreader-tool | 2026-01-04 | Python | Intelligence tiling | Foundational |
| webgpu-profiler | 2026-01-09 | TypeScript | GPU monitoring | Active |
| cocapn | 2026-02-28 | Python | Agent philosophy | Manifesto |
| polln | 2026-03-06 | TypeScript | Spreadsheet viz | Experimental |
| AI-Writings | 2026-03-08 | Python | Creative archive | Archive |
| Lucineer | 2026-03-13 | Python | Search engine | Early |
| Equipment-Consensus-Engine | 2026-03-13 | TypeScript | Multi-agent deliberation | Mature |
| Equipment-Escalation-Router | 2026-03-13 | TypeScript | LLM routing | Mature |
| dodecet-encoder | 2026-03-16 | Rust | 12-fold ML encoder | Research |
| AIR | 2026-03-18 | Python | Nightly synthesis | Active |
| constraint-theory-core | 2026-03-27 | Rust | Manifold snapping | Core |

---

*"Before the fleet had ships, it had equipment. Before the ships had names, the equipment had purposes."*
