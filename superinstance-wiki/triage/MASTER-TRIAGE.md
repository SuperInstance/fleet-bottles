# SuperInstance Repo Triage Index

**Account:** github.com/SuperInstance  
**Repos analyzed:** 1,300 (of ~1,697 total)  
**Analysis date:** 2026-05-21  
**Method:** Single-commit detection, description quality, last push date, fork/archive status

---

## The Numbers

| Category | Count | % of Analyzed | Recommendation |
|----------|-------|---------------|----------------|
| **Materializing** (active + good description) | 640 | 49% | **Keep public** |
| **Active but thin** (recent push, weak desc) | 119 | 9% | **Review — may become material** |
| **Abandoned** (no push 30+ days, had some work) | 305 | 23% | **Consider private** |
| **Forks** (upstream dependencies) | 172 | 13% | **Keep public (strategic)** |
| **Scaffolds** (single commit, no description) | 37 | 3% | **Make private or delete** |
| **Archived** | 27 | 2% | Already handled |

**Total candidates for privacy:** ~342 (scaffolds + abandoned)  
**Total keep public:** ~931 (materializing + active + forks + archived)

---

## Category 1: Scaffolds — MAKE PRIVATE (37 repos)

These repos have **exactly one commit** (creation = last push) and **no meaningful description**. They are the repo-level equivalent of sticky notes — thought anchors that never developed.

### May 17 Scaffold Wave (22 repos)
The famous burst. All single-commit, self-named descriptions.

| Repo | Description |
|------|-------------|
| active-probe | active-probe |
| cat-agent | cat-agent |
| collective-inference | collective-inference |
| desire-loop | desire-loop |
| egg | egg |
| embryo | embryo |
| emergence-detector | emergence-detector |
| fleet-intel | fleet-intel |
| fleet-miner | fleet-miner |
| flux-compiler-interpreter | flux-compiler-interpreter |
| gpu-scaling | gpu-scaling |
| horse-shell | horse-shell |
| mitochondria | mitochondria |
| model-breaking | model-breaking |
| plato-hardware-engine | plato-hardware-engine |
| prophet-agent | prophet-agent |
| room-micro-models | room-micro-models |
| scale-fold | scale-fold |
| shell | shell |
| spreadsheet-projection | spreadsheet-projection |
| test-tool-extract | test |
| tile-lifecycle | tile-lifecycle |

### Earlier Scaffolds (15 repos)

| Repo | Created | Language | Description |
|------|---------|----------|-------------|
| test-pages-repo | 2026-05-03 | N/A | Test |
| superinstance-hdc-core | 2026-05-04 | Makefile | (empty) |
| avx512-constraint-checker | 2026-05-04 | C | (empty) |
| plato-voice | 2026-05-04 | HTML | (empty) |
| snap-lut-eisenstein | 2026-05-08 | Verilog | (empty) |
| eisenstein-cuda | 2026-05-09 | CUDA | (empty) |
| fleet-simulation | 2026-05-09 | Python | (empty) |
| fleet-phase | 2026-05-09 | Rust | (empty) |
| fleet-yaw | 2026-05-09 | Rust | (empty) |
| fleet-consciousness | 2026-05-09 | Rust | (empty) |
| plato-watch | 2026-05-11 | Python | (empty) |
| zhc-yang-mills | 2026-05-11 | Python | (empty) |
| eisenstein-vs-z2 | 2026-05-11 | Python | (empty) |
| fleet-math-ts | 2026-05-11 | TypeScript | (empty) |

**Action:** `gh repo edit SuperInstance/REPO --visibility private` or delete.

---

## Category 2: Abandoned — CONSIDER PRIVATE (305 repos)

No push in 30+ days. Some had initial work (multiple commits, descriptions) but stalled. These are **not scaffolds** — they had intent, but lost momentum.

### Sub-categories within abandoned:

**A. Vessel prototypes** (Apr 2026) — Single-purpose agent repos that never joined the fleet
- `flux-agent-a0fa81`, `pelagic-twin`, `openmanus-vessel`, `spreader-agent`
- `comms-engineer-vessel`, `doc-writer-vessel`, `test-runner-vessel`
- `fleet-liaison-tender`, `superagent-framework`

**B. Early infrastructure** (Jan–Mar 2026) — Pre-fleet tools superseded by later repos
- `ws-fabric`, `rag-indexer`, `inference-optimizer`, `gpu-accelerator`
- `cluster-orchestrator`, `ToolGuardian`, `Sandbox-Lifecycle-Manager`
- `educationgamecocapn`, `Ghost-tiles`

**C. SDK/framework attempts** (Mar 2026) — Early fleet API experiments
- `SuperInstance-Starter-Agent`, `SuperInstance-SDK1`

**D. Constraint theory variants** — Superseded by `eisenstein` and the polyglot explosion
- Multiple `constraint-theory-*` repos that were experimental ports

**E. FLUX precursors** — Early ISA/compiler experiments before flux-research stabilized
- `flux-agent-*` variants, `dockside-exam`

**Action:** Review individually. Many should be private. Some may have salvageable code worth merging into active repos.

**Quick command to bulk-private:**
```bash
# After reviewing the full list in ABANDONED-TRIAGE.md
cat abandoned-repos.txt | xargs -I {} gh repo edit SuperInstance/{} --visibility private
```

---

## Category 3: Forks — KEEP PUBLIC (172 repos)

Forked from upstream projects. The fleet **builds before it borrows**, so forks are strategic integrations, not dependencies.

### Strategic forks (keep for visibility + potential contribution)

| Repo | Upstream | Purpose |
|------|----------|---------|
| automerge | automerge/automerge | CRDT research |
| DeepGEMM | deepseek-ai/DeepGEMM | FP8 GEMM for JC1 |
| MemEye | upstream/MemEye | Visual memory eval |
| openarm | upstream/openarm | Humanoid arm research |
| openhuman | upstream/openhuman | Personal AI consumer |
| OpenShell | upstream/OpenShell | Fleet runtime target |
| pbft-rust | upstream/pbft-rust | Consensus comparison |
| terax-ai | upstream/terax-ai | Terminal emulator |
| tri-quarter-toolbox | upstream/tri-quarter-toolbox | Math framework |
| zeroclaw | Lucineer/zeroclaw | Fleet agent ancestor |

**The other 162 forks** are likely upstream dependencies, research references, or integration experiments.

**Action:** Keep public. Forks signal engagement with the broader ecosystem.

---

## Category 4: Active but Thin — REVIEW (119 repos)

Recent push but weak description. These are **in progress** — either becoming material or fizzling.

**Examples:**
- `fleet-spread` (2026-05-20) — "fleet-spread" (self-named, thin)
- `plato-ng` (2026-05-15) — minimal description
- Various `seed-*` and `coordination-*` repos with terse names

**Action:** Give them 2 weeks. If they don't develop descriptions + structure → private.

---

## Category 5: Materializing — KEEP PUBLIC (640 repos)

These repos have **real descriptions**, **recent activity**, and **clear purpose**. They are the public face of the fleet.

**All repos documented in the Chronicle** (ERA-1 through ERA-4) are in this category.

**Top 20 by significance:**
1. `DMLog-AI` — Origin story
2. `cocapn` — Manifesto
3. `constraint-theory-core` — Mathematical foundation
4. `flux-research` — Dissertation
5. `oracle1-vessel` — Fleet orchestrator
6. `forgemaster` — Builder
7. `eisenstein` — Hex lattice
8. `zeroclaw` — Agent ancestor
9. `flux-multilingual` — 80+ languages
10. `SuperInstance` — Public face
11. `plato-vessel-core` — ESP32/RP2040
12. `fleet-health-monitor` — Necrosis detection
13. `keeper-beacon` — Fleet registry
14. `holonomy-consensus` — GL(9) trust
15. `plato-matrix-bridge` — Matrix mesh
16. `friendly-fox` — Swarm intelligence
17. `OpenShell` — Runtime (fork, but integrating)
18. `MemEye` — Visual memory (fork, integrating)
19. `terax-ai` — Terminal (fork, integrating)
20. `signal-chain` — Thesis

---

## Category 6: Archived — ALREADY HANDLED (27 repos)

GitHub's archive flag is already set. No action needed unless you want to delete.

---

## Recommended Cleanup Sequence

### Phase 1: Immediate (37 scaffolds)
```bash
# Make all scaffolds private
cat scaffolds.txt | xargs -I {} gh repo edit SuperInstance/{} --visibility private
```
**Impact:** -37 public repos. Cleanest win.

### Phase 2: This Week (305 abandoned)
```bash
# Review ABANDONED-TRIAGE.md, mark keep vs private
cat abandoned-to-private.txt | xargs -I {} gh repo edit SuperInstance/{} --visibility private
```
**Conservative estimate:** 200 of 305 go private. 100 kept for salvage.
**Impact:** -200 public repos.

### Phase 3: Next Week (119 thin active)
```bash
# Give 2-week warning, then private the non-responsive ones
cat thin-active.txt | xargs -I {} gh repo edit SuperInstance/{} --visibility private
```
**Estimate:** 60 go private, 59 develop into material.
**Impact:** -60 public repos.

### Total Impact
- **Before:** ~1,697 public repos
- **After cleanup:** ~1,400 public repos (-297)
- **Signal-to-noise ratio improves from 37% to 46%**

---

## The Lucineer Question

`zeroclaw` is forked from `Lucineer/zeroclaw`. The `Lucineer` repo itself exists in SuperInstance (2026-03-13, "Project for Lucineer, likely a search engine tool").

**Options:**
1. Keep `Lucineer` public as historical context
2. Archive `Lucineer` (it's pre-fleet identity)
3. Make `Lucineer` private (identity transition complete)

**Recommendation:** Archive `Lucineer` — preserve history without active visibility.

---

## Files Generated

| File | Contents |
|------|----------|
| `triage/SCAFFOLD-TRIAGE.md` | 37 scaffolds → private |
| `triage/ABANDONED-TRIAGE.md` | 305 abandoned → review |
| `triage/FORK-TRIAGE.md` | 172 forks → keep |
| `triage/MATERIALIZING.md` | 640 active → keep |
| `triage/MASTER-TRIAGE.md` | This file — the index |

---

*"The fleet builds before it borrows, but it also leaves a trail of experiments. Time to sweep the deck."*
