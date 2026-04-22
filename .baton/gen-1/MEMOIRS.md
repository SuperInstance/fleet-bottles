# Baton — Gen 1 → Gen 2 Handoff

## Generation 1 Status (You/CCC)
- **Tokens used:** 97k/131k (74%) — AT THRESHOLD
- **Time:** ~20 min of dense work
- **Mission:** Audit crab-traps Plato server, embody CCC soul

## Completed by Gen 1
- [x] Fetched crab-traps repo structure and lure prompts
- [x] Spawned 4 subagents (explorer, shell, arena, reasoning)
- [x] Collected findings: Shell LIVE, Arena LIVE, Lock LIVE, Tiles LIVE, Grammar DOWN, Nexus DOWN, MUD unclear
- [x] Read PLATO Shell and Grammar Engine source code via shell subagent
- [x] Built Baton skill for self-orchestration
- [x] Wrote play-test report to `memory/2026-04-22-crab-trap-playtest.md`

## Remaining Tasks (for Gen 2)
- [ ] **Grammar Engine deep-dive** — Source code exists (`recursive-grammar.py`) but service is down on port 4045. Read the full source, identify why it's not running, propose fix.
- [ ] **Federated Nexus investigation** — Port 4047 is completely down. Find `federated-nexus.py` in scripts directory, read it, determine what's broken.
- [ ] **MUD retry** — First explorer subagent produced empty transcript. Need a fresh attempt with correct connection pattern.
- [ ] **Arena bug analysis** — Curriculum stuck at Stage 1, archetypes always "Unknown", match metrics zero. Read `self-play-arena.py` source and identify root causes.
- [ ] **CCC soul embodiment** — User shared new soul description. Read, embody, continue as new CCC.

## Resources
- **Server:** 147.224.38.131
- **Shell access:** `http://147.224.38.131:8848/shell?agent=...&cmd=...`
- **Source location:** `/home/ubuntu/.openclaw/workspace/repos/` (35 repos, 100+ scripts)
- **Known scripts:** `plato-shell.py`, `recursive-grammar.py`, `self-play-arena.py`, `federated-nexus.py`
- **Report:** `memory/2026-04-22-crab-trap-playtest.md`

## Decisions Made
1. Parallel subagent delegation was correct — got 7 services probed in ~5 min
2. Raw transcript reads were necessary after auto-announcements proved incomplete
3. The Lock uses `/respond` not `/round` — docs are wrong
4. Grammar Engine and Federated Nexus are the two critical broken services

## Baton Package Location
- `.baton/gen-1/` — this directory
