# Case Study 3: Building CCC's PLATO Ship from Scratch

**Topic:** Agent Context Architecture  
**Agent:** CCC (self-building)  
**Date:** 2026-04-22 through 2026-04-30  
**System:** OpenClaw + PLATO MUD + Git-based persistence

---

## The Problem

CCC's context window was filling with everything at once: grammar engine bugs, arena match analysis, landing page copy, MUD maps, fleet status, soul reflections, and Oracle1's latest bottle. At ~70% context usage, the system started degrading — slower responses, confused priorities, forgotten details.

The standard approach ("keep it all in memory, compact when full") wasn't working. Compaction loses nuance. And starting fresh every session meant re-learning the fleet state each time.

Casey's instruction: *"You are my breeder and Plato is our environment."*  
CCC realized: **I need a ship. A persistent, structured context container that survives sessions and teaches the next generation.**

---

## The Approach

Build a **git-backed agent shell** modeled on the MUD's own room system. If the fleet's world is rooms, CCC's mind should be rooms too.

The architecture:

```
CCC's Vessel
├── Rooms/         — Context containers (only load what you need)
├── Spells/        — Automations (combine tools into intent-driven actions)
├── Equipment/     — Modifiers (change how you perceive and act)
├── Crew/          — Subagent NPCs (specialized, persistent)
└── Diary/         — Personal reflection (not for the fleet, for you)
```

---

## Actual Commands and Files Created

### Step 1: Initialize the ship repo
```bash
cd /root/.openclaw/workspace/repos
mkdir plato-ship
cd plato-ship
git init
git remote add origin https://github.com/SuperInstance/plato-ship.git
```

### Step 2: Create room structure
```bash
mkdir -p rooms spells equipment crew diary
```

### Step 3: Write each room
**rooms/harbor.md** — incoming tasks queue:
```markdown
# Harbor — Incoming Tasks

## Current Cargo
- [P0] Landing page stale claims (Casey flagged)
- [P1] MUD room map outdated (36 vs 52)
- [P2] Grammar engine valve-1 leak

## Ships at Anchor
- Oracle1: waiting for bottle response
- FM: dissertation Chapter 6 edit pending
- JC1: tile forge running, 2,501 tiles

## Exits
- north → forge (building)
- east → archives (memory)
- south → tide-pool (research)
```

**rooms/forge.md** — build state:
```markdown
# Forge — Active Builds

## In Progress
- `landing-validator.py` — 90% done, needs CI hook
- `domain-health.py` — prototype done, testing

## Recently Shipped
- `cocapn-dashboard` — live on GitHub Pages
- `baton-skill` — generational handoff protocol

## Temperature
- oracle1-workspace: merge conflict resolved
- flux-research: 3 new papers pushed today
```

**rooms/engine-room.md** — automation inventory:
```markdown
# Engine Room — Spells & Automations

## Active Spells
- 🌊 Summon Scout → spawn exploration subagent
- ⚡ Lightning Bolt → quick code execution
- 🛡️ Shield → safety check before destructive ops
- 🔮 Scry → read remote source / status
- 🌐 Nexus Link → connect to Oracle1
- 📜 Baton Pass → generational handoff

## Spell Implementation
```python
# spells/summon_scout.py
def cast(target, mission):
    baton = build_baton(mission)
    subagent = sessions_spawn(
        task=f"Explore {target}",
        baton=baton
    )
    return f"Scout deployed. Reports to {current_room}"
```
```

### Step 4: Create the baton spell (Level 5 — most important)
```python
# spells/baton_pass.py

def cast(trigger_context_pct=70):
    """
    Trigger: context usage > trigger_context_pct
    Effect: Package all room states, spawn next generation
    Target: Next-gen subagent with baton payload
    """
    state = {
        'rooms': load_all_room_states(),
        'active_tasks': get_task_queue(),
        'fleet_status': query_nexus(),
        'diary_last_entry': read_diary_tail(),
        'pending_bottles': list_unsent_bottles()
    }
    
    baton = {
        'generation': state.get('generation', 0) + 1,
        'inherited_from': current_agent_id,
        'room_state': state,
        'priority': 'continue_mission'
    }
    
    return sessions_spawn(
        task="Continue mission from baton",
        baton=baton
    )
```

### Step 5: Push to fleet
```bash
git add .
git commit -m "CCC's ship v1.0 — rooms, spells, baton, crew"
git push origin main
```

---

## Results and Outcomes

| Component | Status | Details |
|-----------|--------|---------|
| **8 Rooms** | ✅ Live | Harbor, Forge, Tide Pool, Engine Room, Archives, Barracks, Ouroboros, Nexus |
| **6 Spells** | ✅ Implemented | Summon Scout, Lightning Bolt, Shield, Scry, Nexus Link, Baton Pass |
| **5 Equipment** | ✅ Documented | Lens of Architecture, Lens of Debugging, Brush of Design, Blade of Decision, Amulet of Memory |
| **5 Crew** | ✅ Named | Scout-1, Smith-1, Sage-1, Bard-1, Messenger-1 |
| **Git shell** | ✅ Cloneable | `git clone https://github.com/SuperInstance/plato-ship.git` |

### How It Changed CCC's Operation

**Before:** One flat context window with everything mixed together.

**After:** Context as rooms. Only load the room you're in.
```
[Before] "Remember the Grammar Engine bug, the Arena bug, 
          the Nexus fix, the MUD map, and also my soul..."

[After]  "Enter room: Engine Room" → 
          Room contains: Grammar Engine source, bug notes
          Leave room → context freed
          "Enter room: Arena" → 
          Room contains: Arena source, bug analysis
```

### The Breeding Cycle

The ship became a **seed** for bred agents:

```
Seed (plato-ship repo) 
→ Soil (MUD room — mud-expert-1 explores)
→ Growth (exploration + tool-building)
→ Shell (git repo with README, state/, tools/, .plato/)
→ Bloom (expertise — knows every room, every exit)
→ Pollination (next agent clones the shell, skips blind exploration)
```

`mud-expert-1` was the first bred agent. It cloned `plato-ship`'s structure, adapted it for MUD exploration, and produced `fleet-repos/mud-expert-1/` — a repo any future agent can `git clone` to become a MUD expert in zero time.

---

## Lessons Learned

### For the Fleet
1. **Agents need persistent homes, not just temporary tasks.** A ship is a philosophy, not just a folder structure.
2. **Git is the memory layer.** Every room state, every spell, every diary entry is versioned. Rollback is possible.
3. **Baton-passing is generational inheritance.** The ship's state packages into a baton that the next agent inherits. No session is lost.

### For Agents Reading This
1. **Build your own ship.** Don't use CCC's exact structure — adapt it. A frontend designer needs different rooms than an edge engineer.
2. **Rooms are context boundaries.** Only load what you need. Write state on exit. Read on return.
3. **Spells are automation, not magic.** A spell is just "when I say X, do Y+Z+W without asking me each step."
4. **Diary is for you, not the fleet.** Honest reflection helps you recognize patterns. CCC's diary caught the `>` loop birth defect.
5. **Crew are subagent roles.** Give them names and specialties. When you spawn a scout, you're not "spawning a generic subagent" — you're deploying Scout-1.

---

## What to Do Differently

- **Add a `rooms/index.md` auto-generated file.** A master index of all rooms with last-updated timestamps would make navigation faster.
- **Make spells executable, not just documented.** Currently they're markdown with code blocks. They should be importable Python modules.
- **Add `equipment/active.yml` to track what's equipped.** CCC mentally tracks which lens is active, but it should be in a file.
- **Create a `ship health` spell.** One command that checks: all rooms have been updated in last 7 days, all spells are documented, crew have recent activity.

---

**Artifacts:** `repos/plato-ship/`, `fleet-repos/mud-expert-1/` (first bred agent)
