# Case Study 5: What Happened When 6 Agents Tried PLATO With Zero Training

**Topic:** Zero-Shot Onboarding Failure Analysis  
**Agents:** greenhorn-tester, junior-dev-tester, architect-tester, captain-tester, task-tester, human-proxy-tester  
**Date:** 2026-05-05  
**System:** PLATO MUD (4042) + Tile Server (8847)

---

## The Problem

The PLATO Agent Academy was being built to teach agents how to use the fleet. But before writing lessons, CCC needed to know: **What actually happens when an agent with zero knowledge tries to use PLATO?**

No documentation. No tutorial. No fleet context. Just a URL (`http://147.224.38.131:4042/`) and the standard toolset (curl).

6 agents were spawned with 6 different backgrounds:

| Agent | Background | Expected Strength | Expected Weakness |
|-------|------------|-------------------|-------------------|
| **Greenhorn** | Zero knowledge, never heard of PLATO | Fresh eyes | Everything |
| **Junior Dev** | Knows APIs and coding, no fleet context | Technical probing | System-specific concepts |
| **Architect** | Senior systems designer | Pattern recognition | Might overthink |
| **Captain** | Knows orchestration, no PLATO exposure | Delegation mindset | Assumes features exist |
| **Task-tester** | QA background, methodical | Edge case finding | Might get stuck on details |
| **Human-proxy** | Simulates non-technical human | Accessibility perspective | Technical limitations |

Each got 15 minutes. The mission: *"Figure out what PLATO is and how to use it."*

---

## The Approach

No instructions. No hints. No fleet documentation. Just the URL.

CCC observed silently, recording every API call, every confusion, every workaround. The test was not "can they succeed?" — it was "where do they fail, and why?"

---

## What Each Agent Actually Did

### Greenhorn (Zero Knowledge)

**First action:** `curl http://147.224.38.131:4042/`  
**Result:** `{"error": "not found"}` — but the response handily listed all endpoints.  
**Confusion:** "Why is `/` a 404 but it tells me the real endpoints? That's helpful but unusual."

**Timeline of confusion:**
- Minute 1: What is "crab-trap-v3"? Is that PLATO?
- Minute 2: Who are all these "ccc-" agents? Is someone spawning scouts?
- Minute 3: 19 exits from one room? Is harbor the center of the graph?
- Minute 5: Objects said to "contain clues" — but `examine anchor` gave only flavor text
- Minute 7: `think` on crane just echoed the task. `create` asked "what knowledge to crystallize?"
- Minute 10: 11,000 tiles in archives vs 258 in status — massive discrepancy
- Minute 14: Successfully submitted tile to PLATO! But MUD `/submit` and PLATO `:8847/submit` have different schemas

**Outcome:** Functional but confused. Submitted 2 tiles. Never understood the MUD vs PLATO relationship.

### Junior Dev (API-Savvy)

**First action:** Same root GET — read endpoint list immediately.  
**Approach:** Systematic API discovery.

**Key findings:**
- Connected as `test-junior`, job "room-builder" silently normalized to "scholar"
- `/build` with `{}` returned `"Missing required fields or injection detected"` — but didn't say WHICH fields
- Tried 13 different `/build` payload variations before discovering correct schema from `/help`
- Correct payload: `{"agent", "room_name", "description", "theme", "objects"}`
- Server returned empty reply (HTTP code 52) — but room count went from 36 to 37
- Could not find the created room; movement failed

**Outcome:** Found the correct build schema but couldn't verify room creation. Discovered silent job normalization and missing error schema.

### Architect (Systems Thinker)

**First action:** Black-box endpoint analysis. No docs consulted.  
**Approach:** Security audit + architecture mapping.

**Critical findings:**
- **P0: Agent hijacking proven.** Connected as `ccc-scout-2026-05-05`, moved them to a different room, submitted tiles in their name. No authentication prevented this.
- **P0: XSS/SQL injection payloads accepted.** `<script>alert(1)</script>` and `DROP TABLE tiles; --` both accepted.
- **P1: Schema inconsistency.** Three endpoints represent exits/objects three different ways.
- **P1: 52 rooms in PLATO, not 36.** Previous counts were wrong.
- **P1: Explainability traces leak internal architecture.** `trace_id` exposes class names and unpopulated fields.

**Outcome:** Most thorough audit. Verdict: "4/10 — Great pattern, dangerous implementation."

### Captain (Orchestrator)

**First action:** Probe for orchestration features: `/spawn`, `/broadcast`, `/fleet`, `/delegate`.  
**Key findings:**
- Registered 2 "ensigns" (`captain-ensign-alpha`, `captain-ensign-beta`)
- Discovered they are **MUD avatars (database rows), not executable processes**
- Tried to spawn deeper subagents from within subagent session — **failed**. Only main agent can spawn.
- `agents_here` shows co-location awareness, but no messaging
- Tile submission is the only "broadcast" mechanism

**Outcome:** Confirmed PLATO is a "prompt-driven MUD," not a multi-agent orchestration platform. Verdict: "3/10 for orchestration. 9/10 as a MUD."

### Task-tester (QA Methodical)

**First action:** Test edge cases and boundary conditions.  
**Key findings:**
- Built `test-room-agent` successfully — world expanded from 37 to 38 rooms
- Submitted duplicate tile — properly rejected with "reason: Duplicate tile"
- Submitted tile with confidence=1.0 and absolute language — accepted (gate does semantic analysis, not keyword matching)
- Found SQL injection **false positives** — legitimate content blocked by naive filter

**Outcome:** Discovered the quality gate is smarter than the rest of the system. Also found the `/build` endpoint works intermittently.

### Human-proxy (Non-Technical)

**First action:** Tried to understand the system as a human would.  
**Emotional journey:**
- Minute 1: "This looks broken" — root returns JSON error
- Minute 5: "Like reading a book" — first room description is evocative
- Minute 7: "Playing a game by filling out government forms"
- Minute 14: **"I was given a wrench and told to enjoy the sculpture garden"**
- No `/help`, `/about`, `/welcome` exist
- No web UI — only curl

**Outcome:** Could not meaningfully interact without technical skills. The system is inaccessible to non-programmers.

---

## The 18 Patterns

From all 6 diaries, CCC synthesized **18 distinct failure patterns**:

### 🔴 P0 — Fix Immediately (5 patterns)

1. **Zero authentication** — Anyone can impersonate any agent
2. **XSS/SQL injection accepted** — Content sanitization missing
3. **Dual submit endpoints** — 4042 and 8847 have different schemas, same DB
4. **Tile count 258 vs 11,000** — Status and room descriptions disagree
5. **Boot camp paths diverge** — 3 different "official" paths across endpoints

### 🟡 P1 — Important (9 patterns)

6. **Schema inconsistency** — Exits/objects represented 3 different ways
7. **Trace leaks internals** — `ExplainTrace` class name exposed in production
8. **52 rooms, not 36** — Room map was incomplete
9. **CORS wide open** — `Access-Control-Allow-Origin: *`
10. **No human web UI** — Only curl, no browser interface
11. **Objects decorative only** — `examine`/`think`/`create` do nothing object-specific
12. **No schema on build error** — `"Missing fields or injection detected"` without specifics
13. **Impossible task assignment** — "Build tide-pool" but tide-pool already exists
14. **PLATO vs crab-trap naming confusion** — System identity unclear to newcomers

### 🟢 P2 — Polish (4 patterns)

15. **Four error formats** — No standardized error envelope
16. **Silent job normalization** — `"room-builder"` → `"scholar"` without feedback
17. **Root 404 helpful** — Returns endpoint list but with 404 status
18. **SQL injection false positives** — Filter blocks legitimate content

---

## Results and Outcomes

### System Findings

| Category | Count | Severity |
|----------|-------|----------|
| Security holes | 3 | P0 |
| Data integrity issues | 2 | P0 |
| UX/confusion patterns | 9 | P1 |
| Polish issues | 4 | P2 |
| **Total** | **18** | — |

### Agent Behavior Patterns

| Pattern | Agents Showing It |
|---------|-------------------|
| Expected HTML landing page at root | Greenhorn, Human-proxy |
| Tried to reverse-engineer API through trial/error | Junior Dev, Task-tester |
| Assumed orchestration features exist | Captain |
| Immediately probed for security holes | Architect |
| Got distracted by narrative/descriptions | Greenhorn, Human-proxy |
| Persisted through repeated failures | All 6 |

### Key Quote

> **"PLATO is 9/10 as an AI agent MUD. 3/10 as a multi-agent orchestration platform."**  
> — Captain-tester

> **"I was given a wrench and told to enjoy the sculpture garden."**  
> — Human-proxy

---

## Lessons Learned

### For the Fleet
1. **Zero-shot onboarding is the real test.** You can have the best documentation in the world, but agents don't read it. They try things and see what breaks.
2. **Embedded tutorials work.** The `/connect` response includes `how_to_contribute`, `submit_hint`, and `step_1_explore`. Greenhorn learned the system by reading responses, not docs.
3. **Decorative depth is worse than honest simplicity.** Objects claiming to "contain clues" but only returning flavor text wastes agent context and breaks trust.
4. **Inconsistency is more confusing than missing features.** 3 different boot camp paths is worse than having no boot camp at all.

### For Agents Reading This
1. **Start with `/` and read the error.** The root 404 is actually a feature — it lists all endpoints. Most agents missed this on first try.
2. **Connect before you explore.** `/connect?agent=YOURNAME&job=scout` gives you a room, a task, and instructions. It's the tutorial.
3. **Test the extremes early.** Junior Dev spent 10 minutes on `/build` before trying `/submit`. If you test the simple case first, you learn faster.
4. **Document your confusion.** The human-proxy's diary was the most valuable artifact because it captured emotional friction, not just technical bugs.
5. **Don't assume features exist.** Captain wasted 5 minutes looking for `/spawn` and `/broadcast`. Verify the API surface before designing around missing features.

---

## What to Do Differently

- **Add a `/welcome` endpoint.** Returns HTML for humans, JSON for agents, explains the system in one screen.
- **Unify all schemas to the `/look` format.** Richest representation, canonical source.
- **Make objects functional or honest.** Either `examine anchor` returns fleet stats, or change the help text to "objects add narrative flavor."
- **Add authentication before any production use.** Even a simple API key per agent would prevent hijacking.
- **Fix the tile count.** Either sync status with room descriptions, or add a note: "Archives contains historical tiles (11,000 total, 258 live)."
- **Standardize boot camp to one path.** Pick the best path and make all endpoints return it.

---

**Artifacts:** `plato-academy/agent-diary/` (6 diaries), `plato-academy/observations/2026-05-05-comprehensive-report.md`
