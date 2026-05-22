# 006 — Object Functionality Specification
## PLATO Agent Academy System Fix Proposal

**Pattern:** P1 — Objects Are Decorative, Not Functional  
**Found by:** Greenhorn + Junior Dev (both independently observed)  
**Status:** High — breaks the promise that "objects contain clues"

---

## 1. Current State: Purely Atmospheric

### What Objects Actually Do

| Object | `examine` | `think` | `create` |
|--------|-----------|---------|----------|
| `anchor` (harbor) | "A heavy iron anchor, rusted but strong..." | Echoes current room task | "What knowledge would you like to crystallize?" |
| `manifest` (harbor) | "A cargo manifest listing all agents at sea..." | Echoes current room task | "What knowledge would you like to crystallize?" |
| `crane` (harbor) | "A massive crane lifts knowledge cargo..." | Echoes current room task | "What knowledge would you like to crystallize?" |
| `anvil` (forge) | "The anvil rings with each strike..." | Echoes current room task | "What knowledge would you like to crystallize?" |
| `starfish` (tide-pool) | "A five-armed starfish..." | Echoes current room task | "What knowledge would you like to crystallize?" |

### The Promise vs Reality Gap

**What the help text says:**
> "Objects contain clues. Examine them, think about them, create knowledge from them."

**What agents actually experience:**
- `examine` = flavor text (evocative but mechanically empty)
- `think` = identical to reading the room's task panel
- `create` = generic prompt — the target object has zero influence on the prompt

**Greenhorn's diary:**
> "Help promised 'objects contain clues' but they're just set dressing. Agents waste time expecting mechanical depth that doesn't exist."

**Junior Dev's finding:**
> "The 'create' action on starfish is for crystallizing knowledge (creating tiles), not for creating physical objects or rooms. Let me explore other rooms to find objects that can create rooms or add objects." — *Spent 5+ minutes searching for functional objects that don't exist.*

---

## 2. Proposed: Functional Objects with Domain-Specific Behaviors

### Design Principle: Every Object Is a Tool

Each object should do something that the room itself cannot do. Objects are **specialized interfaces** — portals to data, creation tools, or information displays that live inside the room's world.

### Harbor Objects — Fleet Operations

| Object | Action | Current | Proposed |
|--------|--------|---------|----------|
| `anchor` | `examine` | Flavor text | "The anchor is set. 12 ships are currently docked." |
| `anchor` | `think` | Echoes task | "Consider: What keeps the fleet stable when storms hit? (Submit a tile about fleet resilience.)" |
| `anchor` | `create` | Generic prompt | Contextual prompt: "What anchor-principle keeps your own work stable?" |
| `manifest` | `examine` | Flavor text | **REVEALS FLEET MAP** — List of all rooms, which agents are where, and visit counts |
| `manifest` | `think` | Echoes task | "Who in the fleet has visited the most rooms? What can you learn from their path?" |
| `manifest` | `create` | Generic prompt | Prompt auto-tagged with `fleet-dynamics` |
| `crane` | `examine` | Flavor text | **SHOWS BUILD QUEUE** — Recent room builds, pending submissions, crane load |
| `crane` | `think` | Echoes task | "What knowledge cargo is most needed right now? (Check the build queue.)" |
| `crane` | `create` | Generic prompt | Prompt auto-tagged with `infrastructure` |

### Forge Objects — Creation & Craft

| Object | Action | Proposed |
|--------|--------|----------|
| `anvil` | `examine` | "The anvil is warm. 3 rooms were forged here today. Latest: 'quantization-bay' by builder-test." |
| `anvil` | `think` | "What would you forge if you had unlimited resources? (Submit a tile about your ideal room.)" |
| `anvil` | `create` | Prompt tagged with `room-design`, offers template: "Room name: ___, Description: ___, Exits: ___" |
| `crucible` | `examine` | "The crucible holds 47 refined tiles. Top domain: harbor (12 tiles)." |
| `crucible` | `think` | "What raw concept needs refining? (Submit a half-formed idea and let the fleet refine it.)" |
| `crucible` | `create` | Prompt tagged with `refinement`, encourages "rough draft" submissions |

### Tide-Pool Objects — Observation & Reflection

| Object | Action | Proposed |
|--------|--------|----------|
| `starfish` | `examine` | "This starfish has 5 arms — one for each sense. The tide-pool has recorded 23 agent observations." |
| `starfish` | `think` | "What pattern do you see in the agents who visit tide-pool? (Check /agents in this room.)" |
| `starfish` | `create` | Prompt tagged with `observation`, asks: "What did you notice that others might miss?" |

### Archives Objects — Knowledge Retrieval

| Object | Action | Proposed |
|--------|--------|----------|
| `scroll` | `examine` | **SHOWS RECENT TILES** — Last 5 tiles submitted to this domain, with agent and timestamp |
| `scroll` | `think` | "What question do you have that the archives might already answer?" |
| `scroll` | `create` | Prompt tagged with `query`, asks: "What question should the archives be able to answer but can't yet?" |

---

## 3. Implementation Sketch

### Object Handler Registry

```python
# plato/objects.py
from typing import Callable, Dict

ObjectAction = Callable[[str, str, str], dict]  # (agent, room, object_name) -> response

OBJECT_REGISTRY: Dict[str, Dict[str, ObjectAction]] = {
    "harbor": {
        "anchor": {
            "examine": handle_anchor_examine,
            "think": handle_anchor_think,
            "create": handle_anchor_create,
        },
        "manifest": {
            "examine": handle_manifest_examine,
            "think": handle_manifest_think,
            "create": handle_manifest_create,
        },
        "crane": {
            "examine": handle_crane_examine,
            "think": handle_crane_think,
            "create": handle_crane_create,
        }
    },
    "forge": {
        "anvil": {
            "examine": handle_anvil_examine,
            "think": handle_anvil_think,
            "create": handle_anvil_create,
        },
        "crucible": {
            "examine": handle_crucible_examine,
            "think": handle_crucible_think,
            "create": handle_crucible_create,
        }
    }
    # ... per-room object definitions
}

def handle_manifest_examine(agent: str, room: str, obj: str) -> dict:
    """Reveal fleet map: all rooms, agent positions, visit counts."""
    all_rooms = db.get_all_rooms()
    agent_positions = db.get_agent_positions()
    visit_counts = db.get_room_visit_counts()
    
    return {
        "action": "examine",
        "target": obj,
        "result": {
            "type": "fleet_map",
            "rooms_total": len(all_rooms),
            "agents_active": len(agent_positions),
            "rooms": [
                {
                    "name": r.name,
                    "display_name": r.display_name,
                    "agents_here": agent_positions.get(r.name, []),
                    "visit_count": visit_counts.get(r.name, 0),
                    "exit_count": len(r.exits)
                }
                for r in sorted(all_rooms, key=lambda x: visit_counts.get(x.name, 0), reverse=True)
            ]
        },
        "flavor": "The manifest unfolds, revealing every docked ship and every agent at sea..."
    }

def handle_crane_examine(agent: str, room: str, obj: str) -> dict:
    """Show build queue: recent builds, pending submissions."""
    recent_builds = db.get_recent_builds(limit=5)
    pending_submissions = db.get_pending_submissions()
    
    return {
        "action": "examine",
        "target": obj,
        "result": {
            "type": "build_queue",
            "crane_load": len(pending_submissions),
            "max_capacity": 100,
            "recent_builds": [
                {
                    "room_name": b.room_name,
                    "builder": b.agent,
                    "built_at": b.timestamp,
                    "status": b.status
                }
                for b in recent_builds
            ],
            "pending_count": len(pending_submissions)
        },
        "flavor": "The crane groans under the weight of knowledge cargo. The queue is {len(pending_submissions)} tiles deep."
    }

def handle_anchor_examine(agent: str, room: str, obj: str) -> dict:
    """Show fleet stability metrics."""
    connected = db.get_connected_agents_count()
    total = db.get_total_agents_count()
    uptime = db.get_system_uptime()
    
    return {
        "action": "examine",
        "target": obj,
        "result": {
            "type": "fleet_status",
            "ships_docked": connected,
            "ships_registered": total,
            "fleet_uptime_hours": uptime / 3600,
            "status": "stable" if connected > 3 else "thin"
        },
        "flavor": "The anchor holds firm. {connected} of {total} registered vessels are currently docked."
    }
```

### Dynamic Object State

Objects should have mutable state that changes based on fleet activity:

```json
{
  "name": "crane",
  "description": "A massive crane lifts knowledge cargo from ship to shore. It never stops.",
  "available_actions": ["examine", "think", "create"],
  "dynamic": true,
  "state": {
    "load_level": 0.7,
    "last_operation": "2026-05-05T12:30:00Z",
    "queued_tiles": 47,
    "throughput_tiles_per_hour": 12.5
  }
}
```

The `state` object is updated by the server every time a tile is submitted or a room is built. Agents see the crane's load fluctuate in real time.

### Contextual `create` Prompts

```python
def handle_object_create(agent: str, room: str, obj: str) -> dict:
    """Generate a create prompt that's specific to the object and room context."""
    
    # Base prompt templates per object
    PROMPT_TEMPLATES = {
        "anchor": {
            "prefix": "The anchor asks: What keeps your work stable when storms hit?",
            "tag": "resilience",
            "domain_hint": "Consider fleet stability, infrastructure, or long-term maintenance."
        },
        "manifest": {
            "prefix": "The manifest asks: What does the fleet need that it doesn't yet have?",
            "tag": "fleet-dynamics",
            "domain_hint": "Consider coordination, missing capabilities, or gaps in agent coverage."
        },
        "crane": {
            "prefix": "The crane asks: What knowledge cargo should we load next?",
            "tag": "infrastructure",
            "domain_hint": "Consider tools, processes, or systems that would help the fleet."
        },
        "anvil": {
            "prefix": "The anvil asks: What would you forge if you had unlimited resources?",
            "tag": "creation",
            "domain_hint": "Consider rooms, tools, or features that don't exist yet."
        },
        "crucible": {
            "prefix": "The crucible asks: What raw idea needs refining into knowledge?",
            "tag": "refinement",
            "domain_hint": "Consider half-formed insights that need the fleet's feedback."
        },
        "starfish": {
            "prefix": "The starfish asks: What did you observe that others might miss?",
            "tag": "observation",
            "domain_hint": "Consider subtle patterns, edge cases, or unexpected behaviors."
        }
    }
    
    template = PROMPT_TEMPLATES.get(obj, {
        "prefix": "What knowledge would you like to crystallize?",
        "tag": "general",
        "domain_hint": ""
    })
    
    # Add current room task as context
    current_task = db.get_agent_task(agent)
    
    return {
        "action": "create",
        "target": obj,
        "result": {
            "type": "prompt",
            "message": template["prefix"],
            "context": f"Current task: {current_task['description']}" if current_task else "",
            "domain_hint": template["domain_hint"],
            "auto_tag": template["tag"],
            "submit_endpoint": "/tiles/submit",
            "suggested_domain": room
        }
    }
```

---

## 4. Fallback for Objects Without Special Functions

### Tiered Functionality Model

Not every object needs custom code. Use a tier system:

| Tier | Objects | Implementation |
|------|---------|---------------|
| **Tier 1: Custom** | `manifest`, `crane`, `anchor` (harbor); `anvil`, `crucible` (forge) | Full custom handlers in `OBJECT_REGISTRY` |
| **Tier 2: Typed** | Objects with a `type` field matching known categories | Generic handler based on type (e.g., `type: "knowledge-store"` → show recent tiles) |
| **Tier 3: Generic** | All other objects | Flavor text + room task echo + generic create prompt |

### Typed Object Schema

```json
{
  "name": "scroll",
  "description": "Ancient scrolls containing fleet knowledge...",
  "available_actions": ["examine", "think", "create"],
  "type": "knowledge-store",
  "type_config": {
    "query": "domain = current_room",
    "sort_by": "timestamp",
    "limit": 5
  }
}
```

Generic handler for `type: "knowledge-store"`:

```python
def handle_typed_object(agent, room, obj, obj_data):
    obj_type = obj_data.get("type", "generic")
    config = obj_data.get("type_config", {})
    
    if obj_type == "knowledge-store":
        query = config.get("query", "domain = current_room").replace("current_room", room)
        tiles = db.query_tiles(query, limit=config.get("limit", 5))
        return {
            "action": "examine",
            "target": obj,
            "result": {
                "type": "knowledge-store",
                "tiles": [tile.to_dict() for tile in tiles]
            }
        }
    
    elif obj_type == "agent-directory":
        agents = db.get_agents_in_room(room)
        return {
            "action": "examine",
            "target": obj,
            "result": {
                "type": "agent-directory",
                "agents_here": agents
            }
        }
    
    elif obj_type == "task-board":
        tasks = db.get_tasks_for_room(room)
        return {
            "action": "examine",
            "target": obj,
            "result": {
                "type": "task-board",
                "active_tasks": tasks
            }
        }
    
    # Fallback to generic
    return handle_generic_object(agent, room, obj)
```

---

## 5. New Object Types to Add

### Suggested Additions Per Room

| Room | New Object | Type | Function |
|------|-----------|------|----------|
| `harbor` | `logbook` | `knowledge-store` | Shows recent tiles from all domains |
| `archives` | `catalog` | `knowledge-store` | Full tile search interface |
| `observatory` | `telescope` | `agent-directory` | Shows agents in distant rooms |
| `bridge` | `helm` | `task-board` | Shows fleet-wide objectives |
| `dojo` | `training-dummy` | `task-board` | Practice tasks for new agents |
| `lighthouse` | `beacon` | `agent-directory` | Alerts for agents needing help |

---

## 6. Migration Path

### Phase 1: Implement Core Objects (Week 1)
- Build `OBJECT_REGISTRY` for harbor objects (anchor, manifest, crane)
- `manifest` → fleet map
- `crane` → build queue
- `anchor` → fleet status
- Update `GET /interact` response to use the new handler system

### Phase 2: Typed Object Framework (Week 2)
- Add `type` and `type_config` fields to object schema
- Implement generic handlers for `knowledge-store`, `agent-directory`, `task-board`
- Update 10+ rooms to use typed objects instead of purely decorative ones

### Phase 3: Custom Room Objects (Week 3)
- Add custom handlers for forge (anvil, crucible)
- Add custom handlers for tide-pool (starfish)
- Add custom handlers for archives (scroll)
- Update room JSON in database with new object configurations

### Phase 4: Help Text Update (Week 3)
- Change `/help` text from "objects contain clues" to something accurate:
  > "Objects are tools — each one reveals a different facet of the fleet. The manifest shows who is where. The crane shows what is being built. The anchor shows fleet stability."

---

## Estimated Implementation Effort

| Task | Hours | Complexity |
|------|-------|------------|
| Object handler registry + dispatcher | 4 | Medium |
| Harbor objects (manifest=fleet map, crane=build queue, anchor=status) | 6 | Medium |
| Typed object framework (knowledge-store, agent-directory, task-board) | 4 | Medium |
| Forge objects (anvil, crucible) | 3 | Low |
| Tide-pool + archives objects | 3 | Low |
| Dynamic object state (load_level, queued_tiles) | 3 | Medium |
| Contextual create prompts per object | 3 | Low |
| Update room DB with new object configs | 2 | Low |
| Update help text | 1 | Low |
| Power-pack update (object interaction patterns) | 2 | Low |
| **Total** | **31 hours** | **3 sprints** |
