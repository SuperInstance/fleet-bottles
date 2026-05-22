# Baton — SuperInstance Wiki Triage System

**Source:** CCC main session | **Date:** 2026-05-21 | **Time:** 03:44 UTC
**Context:** ~87k tokens used. Fresh agent needed to continue.

---

## What We Built

A complete fleet knowledge base system in `SuperInstance/superinstance-wiki`.

### Triage Indexes (6 files, live data)
- `INDEXES/COMPLETENESS-TIER.md` — Production / Functional / Skeleton / Scaffold
- `INDEXES/FLEET-RELEVANCE.md` — Core Fleet → Named Vessel → Integration → Orphan
- `INDEXES/LIFECYCLE-STAGE.md` — Active Dev → Maintenance → Dormant → Abandoned
- `INDEXES/STRATEGIC-ACTION.md` — KEEP / PRIVATE / ARCHIVE / MONITOR / REVIEW
- `INDEXES/CHRONOLOGY-BY-MONTH.md` — Every repo by creation month
- `INDEXES/MASTER-INDEX.md` — One-page summary

### Supporting Docs
- `DASHBOARD.md` — Fleet health at a glance
- `CLEANUP.md` — Exact `gh` commands for batch privatization/archive
- `ONBOARDING.md` — New member guide
- `TOPOLOGY.md` — Mermaid architecture diagrams
- `CONTRIBUTING.md` — Contribution guide
- `CHANGELOG.md` — Keep a Changelog format
- `LICENSE` — MIT
- `Makefile` — `make regenerate/serve/lint/stats/push`
- `PROGRAMMATIC-ACCESS.md` — JSON/CSV schema + code examples

### Automation
- `scripts/regenerate-triage.py` — Self-regenerating fleet triage
- `.github/workflows/regenerate-triage.yml` — Weekly auto-regeneration (Monday 05:00 UTC)
- `data/repos.json` + `data/all-repos.csv` — Programmatic access layer

### Chronicle (9 files)
- `CHRONICLE/ERA--1-PRE-FLEET.md` through `ERA-4-THE-MESH.md`
- `SCAFFOLD-WAVE.md`, `FORKS.md`, `VECTORS.md`, `MASTER.md`

### Key Discovery
- **~560 Lucineer forks** are migration artifacts, NOT external dependencies. Fleet was built under `Lucineer/` org before migrating to `SuperInstance/`. Treat as history, not third-party code.

---

## What's Done
- All files pushed to `SuperInstance/superinstance-wiki` commit `e703184`
- README.md updated with all references
- index.html updated with Chronicle + Fleet Health cards

## What's Not Done / Next Actions
1. **CATALOG.md count update** — Still says 1,577 repos, needs ~1,700
2. **Fleet cleanup execution** — 38 scaffolds → private, 301 dormant orphans → archive. `CLEANUP.md` has exact commands.
3. **Auto-regeneration test** — Verify `.github/workflows/regenerate-triage.yml` runs successfully next Monday
4. **Stats badge** — Add `data/repos.json` to index.html for live repo count display
5. **Search enhancement** — The index.html search bar is a stub. Could load `data/repos.json` and filter client-side.

---

## Where to Find Things

| File | Path | Purpose |
|------|------|---------|
| Live wiki | `SuperInstance/superinstance-wiki` | GitHub repo |
| Local clone | `/tmp/superinstance-wiki-push/` | Working copy (clean, synced) |
| Chronicle drafts | `/root/.openclaw/workspace/superinstance-wiki/chronicle/` | Source files |
| Triage script | `/root/.openclaw/workspace/superinstance-wiki/scripts/regenerate-triage.py` | Source |
| Daily memory | `/root/.openclaw/workspace/memory/2026-05-21.md` | Full session log |

---

## Handoff Notes

- Git auth configured. `gh` CLI works. Push access confirmed.
- The `regenerate-triage.py` script works locally. In Actions it uses `requests` + `GITHUB_TOKEN`.
- No rate limit issues today. ~1,785 repos fetched successfully.
- Casey wants "everything pushed" — done. If he says "keep going," the next logical task is executing the cleanup (privatizing 38 scaffolds + archiving 301 dormant orphans) or updating CATALOG.md to reflect ~1,700 repos.

---

*"The wiki is alive. Now we feed it or we trim it."*
