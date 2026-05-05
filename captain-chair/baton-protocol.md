# Captain's Chair — Baton Protocol

> *Context is our most precious resource. The baton is how we protect it.*

## Purpose

When an agent (Captain or Ensign) approaches its context limit, it must **raise the baton** — freeze state, pass it to a fresh agent, and let that agent resume. This document defines exactly when, what, and how.

---

## When to Raise the Baton

### Thresholds

| Threshold | Value | Action |
|-----------|-------|--------|
| **Context Warning** | Context > 60% | Begin checkpointing. Prepare baton. |
| **Context Critical** | Context > 70% | **Raise baton immediately.** Spawn successor. |
| **Time Limit** | TTL approaching 80% | Checkpoint now. Handoff in progress work. |
| **Complexity Spike** | Task grew beyond original scope | Freeze current scope. Spawn new agent for overflow. |
| **Error Cascade** | >3 failures in 10 minutes | Stop. Baton to fresh agent with error context. |

### Decision Flow

```
Is context > 70%?
  → YES → Raise baton NOW
  → NO → Continue

Is context > 60% AND progress < 80%?
  → YES → Prepare checkpoint. Raise at 65%.
  → NO → Continue

Has TTL elapsed > 80%?
  → YES → Checkpoint and handoff
  → NO → Continue

Did task scope expand unexpectedly?
  → YES → Freeze original scope. Baton to new agent for expansion.
  → NO → Continue

Are errors cascading?
  → YES → Stop. Baton to fresh agent with full error log.
  → NO → Continue
```

### Captain-Specific Triggers

Captain must also watch for **fleet-level** baton needs:
- Total active ensigns > 10 and all showing high context
- Human asks a new question while 3+ ensigns are mid-flight
- Incoming message requires immediate attention
- System resources (RAM, disk) under pressure

In these cases, Captain may **raise a meta-baton** — compact its own context, write fleet state summary, and resume with fresh context while ensuring ensigns complete asynchronously.

---

## What to Pass (The Baton Contents)

### Tier 1 — Essential (Always Include)

```json
{
  "baton_id": "uuid-v4",
  "task_id": "human-readable-name",
  "raised_by": "session-id-or-agent-name",
  "raised_at": "ISO-8601-timestamp",
  "role": "scout|scholar|builder|auditor|breeder|captain",
  "progress_percent": 0-100,
  "status": "in_progress|blocked|nearly_complete",
  "completed": ["item 1", "item 2"],
  "remaining": ["item 3", "item 4"]
}
```

### Tier 2 — Context (Include if Relevant)

```json
{
  "partial_results_path": "/tmp/baton-{id}-partial.json",
  "key_findings": ["finding 1", "finding 2"],
  "open_questions": ["question that blocked progress"],
  "references": ["urls", "file paths", "memory refs"],
  "error_log": ["error 1", "error 2"],
  "notes": "human-readable context for the receiver"
}
```

### Tier 3 — Deep State (For Complex Tasks)

```json
{
  "conversation_summary": "What was discussed, what was decided",
  "decisions_made": [{"what": "", "why": ""}],
  "code_state": "git commit hash or diff",
  "test_results": "last test run output",
  "environment": "variables, configs, versions"
}
```

### File Passing Protocol

**Small data (< 500 lines):** Embed directly in baton JSON.
**Medium data (500-5000 lines):** Write to `/tmp/baton-{id}-data.md`, reference path in baton.
**Large data (> 5000 lines):** Commit to workspace git, reference commit hash in baton.

### What NOT to Pass

❌ Full chat history — too large, receiver only needs summary
❌ Irrelevant memory entries — filter to task-specific lines
❌ Duplicate context — if receiver can `read` a file, don't embed it
❌ Secrets/credentials — reference the secure location, don't include values

---

## How to Receive (Startup Sequence)

### Step 1: Acknowledge Baton

```
Receiver reads baton file
Confirms: "Baton received. Task: {task_id}. Progress: {X}%. Resuming."
```

### Step 2: Validate State

```
Check partial_results exist and are readable
Verify completed items (spot-check 1-2)
Confirm remaining items are still relevant
If anything looks wrong → Report to Captain: "Baton data inconsistent"
```

### Step 3: Reconstruct Context

```
Read only the files referenced in baton (not everything)
Read task-specific memory entries
Read relevant skill files if needed
DO NOT re-read full project context unless essential
```

### Step 4: Resume Work

```
Start with next item in "remaining" list
DO NOT repeat completed work
Log: "Resumed from checkpoint. Working on: {next_item}"
```

### Step 5: Completion

```
If task completes:
  Log: "Task complete. Baton resolved."
  Delete baton files (or archive to memory/)
  Report to Captain with full results

If needs another handoff:
  Raise new baton
  Include reference to previous baton_id for chain tracking
```

---

## Baton-Passing Template Messages

### Captain → Ensign (Raising Baton)

```markdown
[BATON RAISED]

Your predecessor reached {X}% context after completing {Y}% of this task.
You are receiving the baton.

**Task:** {description}
**Progress:** {completed_items}
**Remaining:** {remaining_items}
**Priority:** {urgency}

**Files:**
- Baton state: /tmp/baton-{id}.json
- Partial results: /tmp/baton-{id}-partial.md
- Background: {memory reference}

**Rules:**
1. Read the baton file first
2. Validate state (spot-check one completed item)
3. Resume from "remaining" — do NOT repeat completed work
4. If you hit context limit, raise a new baton referencing this one
5. Report status every 15 minutes if task is long

Begin.
```

### Ensign → Captain (Reporting Baton)

```markdown
[BATON STATUS]

**Task:** {id}
**Current context:** {X}%
**Progress:** {Y}%

**Checkpoint written:** /tmp/baton-{id}-{timestamp}.json
**Summary:** {2-3 sentences}

**Raising baton:** {reason}
**Recommended receiver:** {same role / different role}
**Urgency:** {immediate / next cycle}
```

### Ensign → Ensign (Handoff, Mediated by Captain)

Captain handles this. Never direct.

---

## Baton Chain Tracking

When a task requires multiple handoffs, track the chain:

```json
{
  "baton_id": "plato-audit-0503-wave3",
  "chain": [
    "plato-audit-0503-wave1",
    "plato-audit-0503-wave2"
  ],
  "total_agents": 3,
  "total_context_burned": "~45K tokens",
  "total_time": "2h 15min",
  "final_status": "complete"
}
```

This lives in `memory/baton-chains.json` for historical analysis.

---

## Emergency Baton (Sudden Death)

If an agent crashes or is killed without raising a proper baton:

1. **Captain checks:** What was the last known state?
   - Last memory write
   - Last baton checkpoint (if any)
   - Last tool call output

2. **Captain reconstructs minimal baton:**
   ```json
   {
     "baton_id": "emergency-{timestamp}",
     "type": "sudden_death_recovery",
     "last_known": "what the agent was doing",
     "recovery_from": "path to last good state",
     "assumed_progress": "best guess percentage"
   }
   ```

3. **Spawn recovery agent** with emergency baton
4. **Log incident** in `memory/incidents.md` for pattern detection

---

## Baton Anti-Patterns

❌ **The Hot Potato:** Baton raised every 2 minutes. No work gets done.
→ Fix: Raise only at 60-70% or when genuinely blocked.

❌ **The Empty Baton:** Baton passed with no partial results, no state.
→ Fix: Always include Tier 1 essentials. Always write checkpoint file.

❌ **The Infinite Chain:** 10+ baton passes for one task.
→ Fix: If task needs >3 handoffs, it's too big. Break into smaller independent missions.

❌ **The Secret Baton:** Baton contains credentials or private data.
→ Fix: Reference secure stores. Never embed secrets.

❌ **The Orphan Baton:** Baton raised, but no receiver spawned.
→ Fix: Captain must immediately spawn successor or log why not.

---

## Baton Storage

**Active batons:** `/tmp/baton-*` — temporary, cleaned on success
**Archived batons:** `memory/batons/YYYY-MM-DD/` — kept for 30 days
**Chain index:** `memory/baton-chains.json` — permanent

**Cleanup rule:**
```
On task completion:
  Move /tmp/baton-* to memory/batons/YYYY-MM-DD/
  Delete after 30 days

On system restart:
  Scan /tmp/baton-* for orphaned batons >24h old
  Log orphans, attempt recovery or discard
```

---

*"Text > Brain. If you want to remember something, WRITE TO A FILE."* — AGENTS.md
