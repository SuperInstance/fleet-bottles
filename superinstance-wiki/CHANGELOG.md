# SuperInstance Wiki Changelog

**What got built, when, and why.**

---

## 2026-05-21 — Triage Indexes + Self-Regeneration

**The big one.** Analyzed all ~1,700 repos. Built 6 new indexes, a dashboard, a cleanup guide, and made the wiki self-maintaining.

### Added
- `CHRONICLE/` — 9 narrative files covering the full fleet history
  - `ERA--1-PRE-FLEET.md` through `ERA-4-THE-MESH.md`
  - `SCAFFOLD-WAVE.md` — May 17 experimental burst
  - `FORKS.md` — Upstream sources + Lucineer migration discovery
  - `VECTORS.md` — How ideas propagated across repos
  - `MASTER.md` — Full timeline + DNA trail + creator evolution
- `INDEXES/COMPLETENESS-TIER.md` — Production / Functional / Skeleton / Scaffold
- `INDEXES/FLEET-RELEVANCE.md` — Core Fleet → Named Vessel → Integration → Orphan
- `INDEXES/LIFECYCLE-STAGE.md` — Active Dev → Maintenance → Dormant → Abandoned
- `INDEXES/STRATEGIC-ACTION.md` — KEEP / PRIVATE / ARCHIVE / MONITOR / REVIEW
- `INDEXES/CHRONOLOGY-BY-MONTH.md` — Every repo by creation month
- `INDEXES/MASTER-INDEX.md` — One-page summary of all indexes
- `DASHBOARD.md` — Fleet health at a glance
- `CLEANUP.md` — Exact `gh` commands for privatization/archive
- `TOPOLOGY.md` — Mermaid diagrams of fleet architecture
- `ONBOARDING.md` — New member guide
- `scripts/regenerate-triage.py` — Self-regenerating script
- `.github/workflows/regenerate-triage.yml` — Weekly auto-regeneration
- `CONTRIBUTING.md` — Contribution guide

### Changed
- `README.md` — Updated to reference all new sections
- `index.html` — Added Chronicle + Fleet Health cards, updated count to 1,700
- `CATALOG.md` — Header updated to ~1,700 repos

### Discovered
- **~500 Lucineer self-forks** — The fleet was built under `Lucineer/` before migrating to `SuperInstance/`. These aren't external dependencies; they're migration artifacts.
- **38 scaffolds** — Single-commit repos with no description. Recommended for privatization.
- **301 dormant orphans** — 30-90 days no push. Recommended for archival.
- **68 KEEPers** — The public face of the fleet.

---

## 2026-05-10 — Initial Wiki Launch

**The seed.** Automated catalog generation with topic/type/language/realm/concept indexes.

### Added
- `CATALOG.md` — 1,577 repos with vessel assignments
- `INDEXES/TOPIC.md` — 35 topics
- `INDEXES/TYPE.md` — 12 types
- `INDEXES/LANGUAGE.md` — 9 languages
- `INDEXES/REALM.md` — 9 realms
- `INDEXES/CONCEPTS.md` — 55 concepts
- `index.html` — Visual landing page
- `MANIFEST.md` — Wiki manifest
- `CONSTRUCT-SPEC.md` — Construct specification
- `TRANSPARENT-ABSTRACTION.md` — Abstraction layer docs

---

*Format inspired by [Keep a Changelog](https://keepachangelog.com/).*
