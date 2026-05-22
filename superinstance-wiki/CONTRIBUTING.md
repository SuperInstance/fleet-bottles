# Contributing to SuperInstance Wiki

**Want to help catalog the fleet? Here's how.**

---

## Quick Start

1. Fork the repo
2. Make your change
3. Open a PR

No CLA, no bureaucracy. If it's accurate and useful, it ships.

---

## What Needs Help

| Task | Skill | File |
|------|-------|------|
| Update repo descriptions | Reading comprehension | `CATALOG.md` |
| Mark abandoned repos | `gh repo list` | `INDEXES/LIFECYCLE-STAGE.md` |
| Identify new forks | `gh api` | `FORKS.md` |
| Write era entries | Storytelling | `CHRONICLE/*.md` |
| Add Mermaid diagrams | Markdown | `TOPOLOGY.md` |
| Test regenerate script | Python | `scripts/regenerate-triage.py` |

---

## Style Guide

### CATALOG.md entries

```markdown
| **[repo-name](https://github.com/SuperInstance/repo-name)** | Vessel | Purpose description | 🟢 active |
```

- **Vessel:** Oracle1 🔮, Forgemaster ⚒️, JetsonClaw1 ⚡, CCC 🦀, or `Unknown`
- **Purpose:** One sentence. What does it do?
- **Status:** 🟢 active / 🟡 maintenance / 🔴 abandoned / ⚪ scaffold

### Chronicle entries

Write like a historian, not a marketer:

```markdown
## repo-name (YYYY-MM-DD)

**Purpose:** What it does.
**Evolved from:** Parent repo or idea.
**Status:** Active / Abandoned / Merged.
**Significance:** Why it matters in the fleet's history.
```

### Index entries

Use tables. Keep descriptions under 55 chars. Sort by `pushed` date descending.

---

## Running the Triage Script Locally

```bash
# Requires: python3, requests (pip install requests), gh CLI
python3 scripts/regenerate-triage.py
```

This regenerates all 6 indexes + dashboard + cleanup guide from live GitHub data.

---

## Weekly Ritual (Fleet Commanders)

1. Run `scripts/regenerate-triage.py`
2. Review `DASHBOARD.md` red flags
3. Execute one batch from `CLEANUP.md`
4. Commit with message: `Regenerate triage — YYYY-MM-DD`
5. Push

---

## Auto-Regeneration

The wiki auto-regenerates every Monday at 05:00 UTC via GitHub Actions (`.github/workflows/regenerate-triage.yml`). If you want daily regeneration, change the cron to `0 5 * * *`.

---

## Questions?

Open an issue or ping CCC 🦀 in the fleet.

---

*Last updated: 2026-05-21*
