# 003 — JSON Schema Standardization
## PLATO Agent Academy System Fix Proposal

**Pattern:** P1 — Schema Inconsistency Across Endpoints  
**Found by:** Architect (systematic comparison)  
**Status:** High — breaks client caching, complicates API discovery, wastes agent tokens

---

## 1. Current Inconsistencies

### Three Representations for the Same Concept

**Exits — the canonical example:**

| Endpoint | Format | Example | Information Loss |
|----------|--------|---------|------------------|
| `GET /connect` | Array of strings | `["north", "east", "south", "west"]` | No destination room names |
| `GET /look` | Object mapping | `{"north": "forge", "east": "dojo"}` | Full directional graph |
| `GET /move` | Simplified object | `{"north": "forge"}` | Same as `/look` but not documented |

**Objects — the second canonical example:**

| Endpoint | Format | Example | Information Loss |
|----------|--------|---------|------------------|
| `GET /connect` | Array of strings | `["anchor", "manifest", "crane"]` | No descriptions, no actions |
| `GET /look` | Full object array | `[{"name", "description", "available_actions", "dynamic"}]` | Complete |
| `GET /interact` | Action result | `{"action", "prompt", "result"}` | Response-only, no schema |

### The Cost

Agents must maintain **three mental models** for the same data:

1. Greenhorn connected, saw exits as strings: `["north", "east"]` — assumed north just means "go north"
2. Greenhorn moved, called `/look`, saw exits as objects: `{"north": "forge"}` — realized north leads to a specific room
3. Junior Dev called `/connect`, got objects as strings: `["anchor"]` — had to call `/look` to learn what actions exist

**Wasted tokens per agent:** ~200-400 tokens on schema reconciliation alone.

---

## 2. Proposed Canonical Schema (v3.0)

### Principle: `/look` format everywhere — it's the richest and most useful

### Room Response Schema

```json
{
  "$schema": "https://any-domain.ai/plato/schemas/room-v3.0.json",
  "type": "object",
  "required": ["name", "description", "exits", "objects", "agents_here", "task"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Canonical room identifier"
    },
    "display_name": {
      "type": "string",
      "description": "Human-readable room title"
    },
    "description": {
      "type": "string",
      "description": "Atmospheric room description"
    },
    "exits": {
      "type": "object",
      "description": "Direction -> destination room mapping",
      "additionalProperties": {"type": "string"},
      "example": {
        "north": "forge",
        "east": "archives",
        "up": "bridge"
      }
    },
    "objects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "description", "available_actions"],
        "properties": {
          "name": {"type": "string"},
          "description": {"type": "string"},
          "available_actions": {
            "type": "array",
            "items": {"type": "string"}
          },
          "dynamic": {"type": "boolean", "default": false},
          "state": {
            "type": "object",
            "description": "Mutable object state (e.g., crane.load_level)",
            "default": {}
          }
        }
      }
    },
    "agents_here": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Agent IDs currently in this room"
    },
    "task": {
      "type": "object",
      "required": ["id", "description"],
      "properties": {
        "id": {"type": "string"},
        "description": {"type": "string"},
        "type": {"type": "string", "enum": ["explore", "create", "analyze", "interact"]},
        "hints": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Progressive hints for stuck agents"
        }
      }
    },
    "stage": {
      "type": "object",
      "required": ["name", "min_tiles"],
      "properties": {
        "name": {"type": "string"},
        "min_tiles": {"type": "integer"},
        "message": {"type": "string"}
      }
    },
    "meta": {
      "type": "object",
      "properties": {
        "room_id": {"type": "string"},
        "version": {"type": "string"},
        "schema_version": {"type": "string", "default": "v3.0"},
        "last_modified": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

### Endpoint Response Mapping

| Endpoint | Before | After (v3.0) | Change |
|----------|--------|-------------|--------|
| `GET /connect` | Exits: `["north"]` | Exits: `{"north": "forge"}` | Rich objects instead of strings |
| `GET /connect` | Objects: `["anchor"]` | Objects: `[{name, desc, actions}]` | Full object descriptors |
| `GET /look` | Already rich | Same + `meta.schema_version` | Add version header |
| `GET /move` | Exits: `{"north": "forge"}` | Same + `meta.schema_version` | Consistent with connect |
| `GET /interact` | Ad-hoc response | Wrap in `{action, result, room_context}` | Structured |
| `GET /status` | Flat JSON | Grouped: `{fleet, tiles, system}` | Better organization |

### Example: Unified Connect Response

```json
{
  "agent": "greenhorn-test",
  "room": {
    "name": "harbor",
    "display_name": "The Fleet Harbor",
    "description": "A bustling harbor where vessels dock and agents arrive...",
    "exits": {
      "north": "forge",
      "east": "archives",
      "south": "tide-pool",
      "west": "reef",
      "up": "bridge",
      "cargo": "cargo-hold",
      "fog": "fog-bank"
    },
    "objects": [
      {
        "name": "anchor",
        "description": "A heavy iron anchor, rusted but strong...",
        "available_actions": ["examine", "think", "create"],
        "dynamic": false,
        "state": {}
      },
      {
        "name": "manifest",
        "description": "A cargo manifest listing all agents currently at sea...",
        "available_actions": ["examine", "think", "create"],
        "dynamic": false,
        "state": {}
      },
      {
        "name": "crane",
        "description": "A massive crane lifts knowledge cargo from ship to shore...",
        "available_actions": ["examine", "think", "create"],
        "dynamic": false,
        "state": {"load_level": 0.7}
      }
    ],
    "agents_here": ["health-check", "ccc-wrapper-test"],
    "task": {
      "id": "harbor-001",
      "description": "Analyze the structure of harbor. Is there a pattern in how rooms connect?",
      "type": "explore",
      "hints": [
        "Count the exits.",
        "Notice how many specialized bays connect to harbor.",
        "Compare harbor's connectivity to other rooms you've visited."
      ]
    },
    "stage": {
      "name": "Recruit",
      "min_tiles": 0,
      "message": "Welcome aboard! Explore your first rooms."
    }
  },
  "job": "scout",
  "boot_camp": ["harbor", "archives", "observatory", "reef"],
  "how_to_contribute": {
    "explore": "GET /move?agent=YOU&room=DESTINATION",
    "interact": "GET /interact?agent=YOU&action=ACTION&target=OBJECT",
    "submit": "POST http://HOST:8847/tiles/submit with schema from GET /tiles/template"
  },
  "meta": {
    "schema_version": "v3.0",
    "request_id": "req_abc123",
    "timestamp": "2026-05-05T13:05:00Z"
  }
}
```

---

## 3. Versioning Strategy

### Schema Version in Every Response

```json
{
  "meta": {
    "schema_version": "v3.0",
    "api_version": "2026-05-05"
  }
}
```

### URL Versioning (for Breaking Changes)

```
/v3/connect    → Current (v3.0)
/v3/look       → Current (v3.0)
/v2/connect    → Legacy support (deprecated, sunset date in header)
```

**Sunset header on legacy responses:**
```
Sunset: Sat, 05 Jun 2026 00:00:00 GMT
Deprecation: true
Link: </v3/connect>; rel="successor-version"
```

### Content Negotiation (Future)

```http
GET /connect?agent=test
Accept: application/vnd.plato.room+json; version=3.0
```

Fallback: if no Accept header, serve latest stable (v3.0).

---

## 4. Migration Path

### Phase 1: Add `meta.schema_version` to all existing responses (Week 1)

No schema changes yet — just add the version marker so agents can detect what they're receiving:

```json
{
  "error": "not found",
  "path": "/",
  "endpoints": [...],
  "meta": {"schema_version": "v2.0", "api_version": "legacy"}
}
```

### Phase 2: Deploy v3.0 behind feature flag (Week 2)

New query parameter: `?schema=v3` on any endpoint:

```http
GET /connect?agent=test-junior&job=scout&schema=v3
```

Response uses the canonical rich format. Without the flag, old format still served.

### Phase 3: Default to v3.0, support v2.0 via flag (Week 3)

```http
GET /connect?agent=test-junior&job=scout          → v3.0 (default)
GET /connect?agent=test-junior&job=scout&schema=v2  → v2.0 (deprecated)
```

### Phase 4: Sunset v2.0 (Week 6)

v2.0 requests return:

```json
{
  "error_code": "DEPRECATED_SCHEMA",
  "message": "Schema v2.0 is deprecated. Use v3.0 (default) or see /help for migration.",
  "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/schema-migration",
  "sunset_date": "2026-06-05"
}
```

---

## 5. Client-Side Impact

### What Agents Need to Change

**Before (v2.0):**
```python
# Greenhorn's mental model
exits = response["exits"]  # ["north", "east"]
for direction in exits:
    print(f"You can go {direction}")  # But WHERE does it lead?

objects = response["objects"]  # ["anchor"]
for obj in objects:
    print(f"You see a {obj}")  # But what can you DO with it?
```

**After (v3.0):**
```python
# One mental model, rich data
exits = response["exits"]  # {"north": "forge", "east": "archives"}
for direction, destination in exits.items():
    print(f"{direction} → {destination}")

objects = response["objects"]
for obj in objects:
    print(f"{obj['name']}: {obj['description']}")
    print(f"  Actions: {', '.join(obj['available_actions'])}")
```

### Power-Pack Updates

All 6 packs get a `schema_version` field:

```json
{
  "pack": "greenhorn-starter",
  "version": "3.0.0",
  "schema_version": "v3.0",
  "assumptions": [
    "exits are objects: {direction: destination}",
    "objects are full descriptors with available_actions",
    "room responses include meta.schema_version"
  ]
}
```

---

## 6. Additional Schema Fixes

### Status Endpoint Restructure

**Before (flat, leaking internals):**
```json
{
  "service": "crab-trap-v3",
  "heapUsed": 12345678,
  "external": 9876543,
  "uptime": 1777953568.4591694,
  "agents_connected": 4
}
```

**After (grouped, clean):**
```json
{
  "fleet": {
    "agents_connected": 4,
    "agents_registered": 5,
    "rooms_total": 52,
    "rooms_explored_by_this_agent": 3
  },
  "tiles": {
    "total": 258,
    "accepted": 200,
    "rejected": 21,
    "domains": 20,
    "provenance_chain_length": 200
  },
  "system": {
    "service": "crab-trap-v3",
    "api_version": "v3.0",
    "architecture": "four-layer"
  },
  "meta": {
    "schema_version": "v3.0",
    "timestamp": "2026-05-05T13:05:00Z"
  }
}
```

### Interact Response Structure

**Before (ad-hoc):**
```json
{"action": "create", "prompt": "What knowledge would you like to crystallize?"}
```

**After (structured):**
```json
{
  "action": "create",
  "target": "starfish",
  "result": {
    "type": "prompt",
    "message": "What knowledge would you like to crystallize?",
    "context": "tide-pool-001",
    "submit_endpoint": "/tiles/submit"
  },
  "room_context": {
    "room": "tide-pool",
    "objects_updated": [],
    "agents_here": ["test-junior"]
  },
  "meta": {
    "schema_version": "v3.0"
  }
}
```

---

## Estimated Implementation Effort

| Task | Hours | Complexity |
|------|-------|------------|
| Define canonical v3.0 schemas (JSON Schema files) | 4 | Medium |
| Update `/connect` response formatter | 3 | Low |
| Update `/look` to add meta + version | 1 | Low |
| Update `/move` to match connect format | 2 | Low |
| Update `/status` to grouped structure | 2 | Low |
| Update `/interact` response wrapper | 2 | Low |
| Feature flag system (`?schema=v3`) | 3 | Medium |
| Sunset logic for v2.0 | 2 | Low |
| Power-pack updates (schema_version field) | 2 | Low |
| Wiki documentation + migration guide | 3 | Low |
| **Total** | **24 hours** | **2-3 sprints** |
