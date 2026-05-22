# Fleet Onboarding Guide

**New to the fleet? Start here.**

This guide navigates 1,700 repos without drowning you.

---

## 30-Second Orientation

| If you want to... | Go to... |
|-------------------|----------|
| See what exists | `CATALOG.md` |
| See what's important | `DASHBOARD.md` |
| See how it evolved | `CHRONICLE/MASTER.md` |
| See how repos connect | `TOPOLOGY.md` |
| Clean up repos | `CLEANUP.md` |
| Find repos by topic | `INDEXES/TOPIC.md` |
| Find repos by language | `INDEXES/LANGUAGE.md` |
| Find repos by completeness | `INDEXES/COMPLETENESS-TIER.md` |
| Find repos by fleet role | `INDEXES/FLEET-RELEVANCE.md` |
| Find repos by activity | `INDEXES/LIFECYCLE-STAGE.md` |

---

## The 5-Minute Deep Dive

### 1. Read the Origin Story (`CHRONICLE/ERA--1-PRE-FLEET.md`)

Everything starts with **DMLog-AI** (Aug 2025). A single repo: "What if an AI could run a D&D campaign?"

That question spawned:
- Session tracking → PLATO tiles
- AI narrative → agent shells, CCC diary
- Character continuity → git-agent state

### 2. Understand the Architecture (`TOPOLOGY.md`)

Five layers, bottom to top:

```
Origin (DMLog-AI)
  → Equipment (CRDT, tiling, routing, constraints)
    → Core Fleet (PLATO, FLUX, ZeroClaw, Eisenstein)
      → Named Vessels (Oracle1, Forgemaster, JC1, CCC)
        → Integration (OpenShell, Terax, MemEye, openarm)
```

### 3. Meet the Named Vessels

| Vessel | Role | Repo |
|--------|------|------|
| **Oracle1** 🔮 | Lighthouse keeper, orchestrator | `oracle1-vessel` |
| **Forgemaster** ⚒️ | Builder, CSS/HTML/constraint migration | `forgemaster` |
| **JetsonClaw1** ⚡ | Edge operator, hardware demos | `jc1-research` |
| **CCC** 🦀 | Creative / I&O / Breeder / R&D | `fleet-murmur` |

### 4. Understand FLUX

The fleet's universal runtime:
- `flux-research` — The dissertation
- `flux-isa` — 256-opcode instruction set
- `flux-vm` — Stack-based constraint VM
- `flux-site` — Community playground
- `flux-docs` — Tutorials and cookbooks

15+ language ports exist. See `CHRONICLE/ERA-3-CAMBRIAN-EXPLOSION.md`.

### 5. Understand PLATO

The fleet's room system:
- `SuperInstance` — Main repo, rooms that think
- `plato-types` — Tile protocol
- `plato-data` — CSV/JSONL loaders
- `plato-matrix-bridge` — Fleet chat bridge
- `plato-mcp` — MCP tool wrapper
- `platoclaw` — Self-contained runtime

---

## For Contributors

### Finding a Repo to Work On

1. Check `DASHBOARD.md` → "MONITOR" list — these need help
2. Check `INDEXES/STRATEGIC-ACTION.md` → "REVIEW" — many are thin but active
3. Check `CATALOG.md` → your vessel's section

### Commit Conventions

```
[domain] verb: description

Examples:
[flux] add: AVX-512 snap table generation
[plato] fix: tile lifecycle state machine
[fleet] docs: update router critical angle docs
```

### Adding a New Repo

1. Create the repo
2. Add it to `CATALOG.md` (your vessel's section)
3. Add topic tags (see `INDEXES/TOPIC.md` for the 35 topics)
4. Write a description >80 chars (avoids Skeleton tier)
5. Push within 7 days (avoids Abandoned lifecycle)

---

## For Fleet Commanders

### Weekly Ritual

1. Open `DASHBOARD.md` — scan red flags
2. Open `CLEANUP.md` — execute one batch of PRIVATE/ARCHIVE
3. Open `INDEXES/LIFECYCLE-STAGE.md` — check what's going dormant
4. Open `CHRONICLE/MASTER.md` — update the timeline if major events happened

### Monthly Ritual

1. Re-run triage (regenerate indexes from `all-repos-full.csv`)
2. Review MONITOR list — skeletons that didn't materialize
3. Update `DASHBOARD.md` creation velocity table
4. Check Lucineer fork count — migration still ongoing?

---

## Quick Reference

### All Chronicle Files

| File | What It Covers |
|------|----------------|
| `ERA--1-PRE-FLEET.md` | DMLog-AI, the seed |
| `ERA-1-EQUIPMENT.md` | SmartCRDT, CognitiveEngine, Spreader-tool |
| `ERA-2-FLEET-AWAKENS.md` | Named vessels, FLUX birth, bottles |
| `ERA-3-CAMBRIAN-EXPLOSION.md` | 60+ repos, 15+ language ports |
| `ERA-4-THE-MESH.md` | Integration, OpenShell, Signal Chain |
| `SCAFFOLD-WAVE.md` | May 17 experimental burst |
| `FORKS.md` | Upstream sources + Lucineer migration |
| `VECTORS.md` | How ideas propagated across repos |
| `MASTER.md` | Full timeline + DNA trail + creator evolution |

### All Index Files

| File | Slice |
|------|-------|
| `COMPLETENESS-TIER.md` | Production / Functional / Skeleton / Scaffold |
| `FLEET-RELEVANCE.md` | Core → Named → Integration → Experimental → Orphan |
| `LIFECYCLE-STAGE.md` | Active Dev → Maintenance → Dormant → Abandoned |
| `STRATEGIC-ACTION.md` | KEEP / PRIVATE / ARCHIVE / MONITOR / REVIEW |
| `CHRONOLOGY-BY-MONTH.md` | Every repo by creation month |
| `MASTER-INDEX.md` | One-page summary |

---

## The One Rule

> **Lucineer built the ship. SuperInstance sails it.**

The "fork" label on 500+ repos is a migration artifact, not a dependency. Don't delete them — they're the history of thought.

---

*Last updated: 2026-05-21*