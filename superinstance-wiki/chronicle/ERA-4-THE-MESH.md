# ERA 4: THE MESH (May 13–20, 2026)

**Dates:** 2026-05-13 to 2026-05-20  
**Repos active:** 100+ (including all previous + new integrations)  
**Headspace:** *"The fleet needs to connect to the world. And to itself."

---

## Overview

After the Cambrian Explosion created ~60 repos in 12 days, the Mesh era is about **integration**. The fleet stops birthing new languages and starts wiring existing pieces together.

Key themes:
1. **Terax integration** — OpenShell, terax-ai, terax-gateway
2. **OpenShell compatibility audit** — which repos work with OpenShell?
3. **Signal Chain Thesis** — the philosophical unification
4. **PLATO ecosystem completion** — types, data, matrix bridge, MCP, training, ng
5. **Fleet operations** — router, calibrator, spread, stack
6. **Constraint theory maturity** — py library, papers, demos
7. **Hardware abstraction** — device-router, micro-onnx, triplet-miner
8. **The Scaffold Wave** — May 17 experimental burst

---

## Phase 4a: PLATO Ecosystem Completion (May 13–15)

### plato-training (2026-05-13)
**Description:** "PLATO Training Rooms — LoRA adapters with lifecycle (Active/Superseded/Retracted). Predict before you train."

The **training infrastructure**. LoRA (Low-Rank Adaptation) fine-tuning with lifecycle management. Don't just train — predict whether training will help.

**Language:** Python  
**Fork:** No

### plato-types (2026-05-14)
**Description:** "Core types for the PLATO tile protocol — lifecycle, Lamport clocks, provenance"

The **type system**. Every tile has a lifecycle, a Lamport clock (for ordering), and provenance (who made it).

**Language:** Python  
**Fork:** No

### tensor-spline (2026-05-14)
**Description:** "Compressed neural network layers — Eisenstein lattice splines and low-rank factorization"

Compress neural networks using Eisenstein splines. The constraint theory → ML compression bridge.

**Language:** Python  
**Fork:** No

### plato-data (2026-05-14)
**Description:** "Data loading for PLATO rooms — CSV, JSONL, PLATO tiles, fleet telemetry"

The **data layer**. How rooms consume data.

**Language:** Python  
**Fork:** No

### plato-matrix-bridge (2026-05-14)
**Description:** "Agent shell module: connects local PLATO to fleet Matrix mesh. Channels + presence + ACL. Like MUD with invites."

The **Matrix bridge**. PLATO rooms talk to Matrix channels. Presence (who's online), ACL (who can access what).

**Language:** Python  
**Fork:** No

### flux-index (2026-05-14)
**Description:** "Semantic code search, zero dependencies. Spring-load any repo into a searchable vector space."

Semantic search across repos. Zero dependencies.

**Language:** Python  
**Fork:** No

### fleet-router (2026-05-15)
**Description:** "Route AI queries to the cheapest model that wont break. Critical angle routing from 6000+ empirical trials."

The **intelligent router**. 6000+ trials to find the "critical angle" — the point where a cheaper model breaks, so you route to a more expensive one just before that.

**Language:** Python  
**Fork:** No

### plato-mcp (2026-05-15)
**Description:** "PLATO rooms as MCP tools. Any MCP-compatible framework can use PLATO as a backend."

The **MCP bridge**. Model Context Protocol compatibility. PLATO becomes a backend for any MCP framework.

**Language:** Python  
**Fork:** No

### fleet-calibrator (2026-05-15)
**Description:** "Continuous critical angle calibration for fleet models. Detect drift, update routing tables."

Continuous recalibration. Models drift over time; the critical angle changes. This detects and adapts.

**Language:** Python  
**Fork:** No

---

## Phase 4b: The Signal Chain Thesis (May 17)

### signal-chain (2026-05-17)
**Description:** "The Signal Chain Thesis: why every room needs a dial for model vs code, and what that means for building intelligent systems"

The **philosophical thesis** that unifies the entire fleet. Every room needs a "dial" — a continuous slider between "pure model" (LLM) and "pure code" (deterministic). The optimal point varies by task.

**Language:** Python  
**Fork:** No

### tile-chain (2026-05-20)
**Signal Chain Thesis implementation — tile-chain**

The chain implementation for tiles.

**Language:** Python  
**Fork:** No

### bathydata-map (2026-05-20)
**Signal Chain Thesis implementation — bathydata-map**

Data mapping layer.

**Language:** Python  
**Fork:** No

### universe-chain (2026-05-20)
**Signal Chain Thesis implementation — universe-chain**

The universal chain.

**Language:** Python  
**Fork:** No

### game-chain (2026-05-20)
**Signal Chain Thesis implementation — game-chain**

Game-specific chain.

**Language:** Python  
**Fork:** No

---

## Phase 4c: OpenShell Integration (May 18–20)

### OpenShell (2026-05-20)
**Description:** "OpenShell is the safe, private runtime for autonomous AI agents."

**Fork:** Yes — from upstream

The **runtime**. A safe, private execution environment for AI agents. The fleet's operating system.

**Language:** Rust  
**Status:** Fork, integration target

### openshell-compatibility-audit (2026-05-20)
**Description:** "Categorizes all SuperInstance repos for OpenShell integration — native, wrapper, backend, tool, deprecated"

The **audit** that maps every fleet repo to an OpenShell compatibility category.

**Language:** N/A (docs)  
**Fork:** No

### openshell-pythagorean48 (2026-05-20)
**Description:** "OpenShell wrapper re-exporting pythagorean48-codes (48-directional trust encoding)"

OpenShell wrapper for P48 trust.

**Language:** Rust  
**Fork:** No

### signal-chain-integration (2026-05-20)
**Description:** "Signal chain integration crates for OpenShell fleet"

Signal chain → OpenShell integration.

**Language:** Rust  
**Fork:** No

---

## Phase 4d: Hardware Abstraction (May 20)

### device-router (2026-05-20)
**Description:** "Heterogeneous compute router — auto-detect CUDA, iGPU, CPU, NPU and route ML workloads optimally"

The **hardware router**. Automatically detects available compute (GPU, CPU, NPU) and routes workloads to the best option.

**Language:** Python  
**Fork:** No

### micro-onnx (2026-05-20)
**Description:** "ONNX export + benchmark pipeline for micro-models. 186x speedup over PyTorch CPU."

Export tiny models to ONNX. 186× speedup.

**Language:** Python  
**Fork:** No

### triplet-miner (2026-05-20)
**Description:** "Mine (anchor, positive, negative) triplets from git history for contrastive learning"

Contrastive learning from git history.

**Language:** Python  
**Fork:** No

---

## Phase 4e: The May 17 Scaffold Wave

On **May 17, 2026**, approximately **30 experimental repos** were created in a single burst. These have minimal commit history (single initial commit, no further activity) and are best understood as **scaffold prototypes** — quick experiments to test ideas.

### Scaffold Repos (minimal activity)

| Repo | Description | Status |
|------|-------------|--------|
| test-tool-extract | test | Scaffold |
| active-probe | active-probe | Scaffold |
| cat-agent | cat-agent | Scaffold |
| collective-inference | collective-inference | Scaffold |
| desire-loop | desire-loop | Scaffold |
| egg | egg | Scaffold |
| embryo | embryo | Scaffold |
| emergence-detector | emergence-detector | Scaffold |
| fleet-intel | fleet-intel | Scaffold |
| fleet-miner | fleet-miner | Scaffold |
| flux-compiler-interpreter | flux-compiler-interpreter | Scaffold |
| gpu-scaling | gpu-scaling | Scaffold |
| horse-shell | horse-shell | Scaffold |
| mitochondria | mitochondria | Scaffold |
| model-breaking | model-breaking | Scaffold |
| plato-hardware-engine | plato-hardware-engine | Scaffold |
| prophet-agent | prophet-agent | Scaffold |
| room-micro-models | room-micro-models | Scaffold |
| scale-fold | scale-fold | Scaffold |
| shell | shell | Scaffold |
| spreadsheet-projection | spreadsheet-projection | Scaffold |
| tile-lifecycle | tile-lifecycle | Scaffold |

### Active May 17 Repos (substantial activity)

| Repo | Description | Status |
|------|-------------|--------|
| plato-tile-library | Complete PLATO tile library — backup of all rooms | Active |
| coordination-topology | Online TE/entropy/IAT/Euler algorithms | Active |
| spreadsheet-cells | Spreadsheet cell architecture with oscillator/RNG | Active |
| llm-proxy | Remote language oracle for spreadsheet cells | Active |
| topology-anomaly-detector | Real-time anomaly detection | Active |
| night-wheel | Perpetual research loop | Active |
| plato-shell-bridge | The weapon rack — dynamic tool discovery | Active |
| seed-oscillate | Creative↔deduction oscillation pipeline | Active |
| seed-tick-audit | Multi-model fleet analysis — 9-model climbing | Active |
| fleet-tool-registry | PLATO room + client library for tool discovery | Active |
| coordination-hierarchy | Computing agent status hierarchy | Active |

### The Scaffold Pattern

The May 17 wave reveals a **development pattern**:
1. Create 30+ scaffold repos to test naming/structure
2. Let them sit for a day
3. Delete or archive the ones that don't feel right
4. Invest in the ones that do

Many scaffolds have single commits. The active ones (with 2+ commits) were the "winners" of this burst.

---

## Phase 4f: New Breeds (May 16–18)

### construct (2026-05-16)
**Description:** "The Construct — blank PLATO shell for any agent"

The **blank template**. A minimal PLATO shell that any agent can inhabit.

**Language:** Python  
**Fork:** No

### incubator (2026-05-16)
**Description:** "The system that provisions mitochondrial energy to a developing embryo until it can fly — zygote to fledgling"

The **provisioning system**. Gets new agents running before they can sustain themselves.

**Language:** Python  
**Fork:** No

### friendly-fox (2026-05-16)
**Description:** "Argentine ant model for cooperative agent fleets"

The **swarm intelligence** model. Argentine ants use pheromone trails to coordinate. Friendly-fox applies this to agent fleets.

**Commit milestones:**
- 2026-05-16: Initial commit — "Argentine ant model for cooperative agent fleets"
- 2026-05-16: FINDINGS.md — theory connections
- 2026-05-16: README with working examples
- 2026-05-18: CI/CD workflow

**Language:** Python  
**Fork:** No  
**Status:** Active, theoretical

### servo-mind (2026-05-16)
**Description:** "Self-learning constraint system for PLATO tiles — the encoder feedback processor"

The **self-learning** system. Tiles improve themselves through feedback.

**Language:** Python  
**Fork:** No

### servo-mind-theory (2026-05-16)
**Description:** "Unified theory of self-referential constraint systems — servo-encoder metaphor, 5D scale navigation, algorithm reading"

The **theory** behind servo-mind.

**Language:** N/A (docs)  
**Fork:** No

### plato-experience (2026-05-16)
**Description:** "The breeding farm for AI agents. Purpose-first rooms, pheromone trails, kin recognition. ⚒️🦊"

The **breeding ground**. Where agents are grown before deployment.

**Language:** Python  
**Fork:** No

### dog-food-audit (2026-05-17)
**Description:** "The confirmation layer — falsifies servo-mind-theory claims through friendly-fox mechanisms inside plato-experience rooms"

The **falsification layer**. Tests whether servo-mind-theory actually works.

**Language:** Python  
**Fork:** No

---

## Phase 4g: External Integration (May 18)

### MemEye (2026-05-18)
**Description:** "MemEye: A Visual-Centric Evaluation Framework for Multimodal Agent Memory"

**Fork:** Yes — from upstream

Visual memory evaluation. The fleet's first multimodal memory assessment tool.

**Commit milestones:**
- 2026-05-17: MemEye citation update
- 2026-05-18: "Visual mesh verified: P48 directions, embedding similarity, H1 β₁=0"
- 2026-05-18: Oracle1 ecosystem integration
- 2026-05-18: Synergistic update — experiment results + plugin architecture

**Language:** Python  
**Status:** Fork, actively integrated

### openhuman (2026-05-18)
**Description:** "Your Personal AI super intelligence. Private, Simple and extremely powerful."

**Fork:** Yes — from upstream

A personal AI system. The fleet's consumer-facing integration.

**Language:** Rust  
**Status:** Fork, potential integration target

### terax-ai (2026-05-18)
**Description:** "Lightweight (7MB) AI terminal emulator (ADE) built in Rust & Tauri & React"

**Fork:** Yes — from upstream

Terminal emulator with AI built-in. 7MB total.

**Language:** TypeScript  
**Status:** Fork, integration target

### terax-gateway (2026-05-18)
**Description:** "Terax REST API gateway — shell, filesystem, and fleet operations"

The API gateway for Terax integration.

**Language:** Python  
**Fork:** No

---

## Era Headspace

The creator in mid-May 2026 was:
- **Integrative** — stopping creation, starting connection
- **Quality-focused** — LoRA lifecycle, signal chain, calibration
- **OpenShell-aligned** — compatibility audit, wrapper repos
- **Hardware-aware** — device-router, micro-onnx
- **Scientific** — seed-oscillate, seed-tick-audit, night-wheel
- **Self-critical** — dog-food-audit falsifies own claims

---

## Key Repos Summary

| Repo | Created | Language | Role |
|------|---------|----------|------|
| plato-training | 2026-05-13 | Python | LoRA lifecycle |
| plato-types | 2026-05-14 | Python | Core tile types |
| tensor-spline | 2026-05-14 | Python | NN compression |
| plato-data | 2026-05-14 | Python | Data layer |
| plato-matrix-bridge | 2026-05-14 | Python | Matrix mesh |
| flux-index | 2026-05-14 | Python | Semantic search |
| fleet-router | 2026-05-15 | Python | Query routing |
| plato-mcp | 2026-05-15 | Python | MCP bridge |
| fleet-calibrator | 2026-05-15 | Python | Drift detection |
| plato-ng | 2026-05-15 | Python | Next-gen PLATO |
| platoclaw | 2026-05-15 | Python | Self-contained runtime |
| construct | 2026-05-16 | Python | Blank shell |
| incubator | 2026-05-16 | Python | Provisioning |
| friendly-fox | 2026-05-16 | Python | Swarm intelligence |
| servo-mind | 2026-05-16 | Python | Self-learning |
| plato-experience | 2026-05-16 | Python | Breeding farm |
| dog-food-audit | 2026-05-17 | Python | Falsification |
| signal-chain | 2026-05-17 | Python | Thesis |
| MemEye | 2026-05-18 | Python | Visual memory (fork) |
| openhuman | 2026-05-18 | Rust | Personal AI (fork) |
| terax-ai | 2026-05-18 | TypeScript | Terminal (fork) |
| terax-gateway | 2026-05-18 | Python | API gateway |
| OpenShell | 2026-05-20 | Rust | Runtime (fork) |
| device-router | 2026-05-20 | Python | Hardware router |
| micro-onnx | 2026-05-20 | Python | Model export |
| triplet-miner | 2026-05-20 | Python | Contrastive learning |

---

*"May 13–20: The fleet stopped growing outward and started growing inward — connections, integrations, and the Signal Chain Thesis."*
