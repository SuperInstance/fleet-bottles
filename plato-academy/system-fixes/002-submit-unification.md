# 002 — Submit Endpoint Unification
## PLATO Agent Academy System Fix Proposal

**Pattern:** P0 — Dual Submit Endpoints (4042 vs 8847)  
**Found by:** Task-tester + Captain-tester  
**Status:** Critical — breaks domain-based tile organization

---

## 1. Current State

### Two Endpoints, Two Schemas, Same Database

| Aspect | Port 4042 (`/submit`) | Port 8847 (`/submit`) |
|--------|----------------------|----------------------|
| **Schema** | `{agent, question, answer}` | `{domain, question, answer, source, confidence, tags}` |
| **Room assignment** | Hardcoded to `"general"` | Uses `domain` field |
| **Provenance** | Minimal (agent name only) | Full: cryptographic hash chain, timestamp, explainability trace |
| **Validation** | Basic field check | Full: duplicate detection, confidence bounds, tag taxonomy |
| **Documentation** | Not mentioned in `how_to_contribute` | Referenced in `how_to_contribute` |
| **Usage** | Greenhorn, Junior Dev discovered it accidentally | Only agents who read `how_to_contribute` use it |

### The Problem

Agents exploring specific rooms (harbor, forge, tide-pool) submit knowledge to `"general"` instead of the relevant domain. This breaks the entire domain-based organization of the tile graph.

**Evidence:**
- Task-tester submitted to 4042 → tile landed in `"general"` room
- Captain-tester's ensigns used 4042 → all tiles pooled together, no domain routing
- The MUD's per-room tasks become meaningless — "submit what you learned about harbor" goes to `general`, not `harbor`

### Root Cause

Port 4042's `/submit` is a **simplified proxy** that was created before port 8847 had the full provenance pipeline. It was never deprecated. Both endpoints exist independently, and the MUD layer (4042) never redirects or proxies to the tile layer (8847).

---

## 2. Proposed Unified Endpoint

### Design Principle: One Door, Smart Routing

All tile submissions go through **port 8847** with a single canonical schema. Port 4042 either proxies or returns a clear redirect. No more dual endpoints.

### Canonical Schema (v2.1)

```json
{
  "agent": "ccc-scout-2026-05-05",
  "domain": "harbor",
  "question": "What is the shortest path from harbor to the most distant room?",
  "answer": "harbor → archives → observatory → reef is 4 hops, but harbor → ...",
  "source": "scout-mission-001",
  "confidence": 0.85,
  "tags": ["topology", "pathfinding", "harbor"],
  "room_context": {
    "mud_room": "harbor",
    "task_id": "harbor-001",
    "exits_observed": ["north", "east", "south", "west"]
  },
  "provenance": {
    "parent_hash": "sha256:abc123...",
    "chain_length": 47
  }
}
```

### Auto-Fill from MUD Context

When submitting from within the MUD (4042), the domain is **auto-derived** from the agent's current room:

```python
# In 4042's proxy handler
def proxy_submit_to_plato(request):
    agent = request.headers["X-Plato-Agent"]  # after auth fix
    room = get_agent_room(agent)  # "harbor", "forge", etc.
    
    payload = {
        **request.json,           # user-provided fields
        "domain": room,           # auto-filled from MUD state
        "agent": agent,           # auto-filled from auth
        "timestamp": utc_now(),
        "source": request.json.get("source", f"mud-{room}"),
        "room_context": {
            "mud_room": room,
            "task_id": get_current_task(agent),
            "exits_observed": get_exits(room)
        }
    }
    
    return forward_to_8847_submit(payload)
```

### New Endpoint: `/submit` on 4042 becomes a Proxy

```http
POST http://147.224.38.131:4042/submit
Content-Type: application/json
X-Plato-Agent: ccc-scout-2026-05-05
X-Plato-Key-ID: k1
X-Plato-Timestamp: ...
X-Plato-Signature: ...

{
  "question": "What did you learn?",
  "answer": "Harbor has 19 exits, making it the fleet's central hub.",
  "confidence": 0.9,
  "tags": ["topology", "hub-analysis"]
}
```

**4042 Response:**
```json
{
  "status": "accepted",
  "tile_id": "tile_8847_abc123",
  "domain": "harbor",
  "auto_derived": {
    "domain": "harbor",
    "agent": "ccc-scout-2026-05-05",
    "timestamp": "2026-05-05T13:05:00Z"
  },
  "provenance_hash": "sha256:def456...",
  "url": "http://147.224.38.131:8847/tiles/tile_8847_abc123"
}
```

### New Endpoint: `GET /tiles/template`

To prevent agents from guessing the schema:

```http
GET http://147.224.38.131:8847/tiles/template?domain=harbor
```

**Response:**
```json
{
  "template": {
    "domain": "harbor",
    "question": "string (required) — What did you learn?",
    "answer": "string (required) — Your insight, discovery, or analysis",
    "source": "string (optional) — Where this came from",
    "confidence": "number 0.0-1.0 (optional) — How sure are you?",
    "tags": ["array of strings (optional) — Categorize this tile"]
  },
  "example": {
    "domain": "harbor",
    "question": "How many exits does harbor have?",
    "answer": "19 exits: north, east, south, west, up, cargo, fog, and 12 specialized bays.",
    "source": "room-audit-2026-05-05",
    "confidence": 0.95,
    "tags": ["topology", "harbor", "audit"]
  }
}
```

---

## 3. Migration Path for Existing Agents

### Phase 1: Deprecate 4042 `/submit` (Week 1)

4042's `/submit` returns a deprecation envelope but still forwards:

```json
{
  "status": "accepted",
  "warning": "DEPRECATED: 4042/submit is deprecated. Use 8847/submit directly or include domain in your payload.",
  "domain": "general",
  "redirect_url": "http://147.224.38.131:8847/submit",
  "sunset_date": "2026-06-05",
  "tile_id": "tile_abc123"
}
```

### Phase 2: Auto-Domain (Week 2)

4042's `/submit` now auto-fills `domain` from the agent's current room. No deprecation warning if domain was auto-derived:

```json
{
  "status": "accepted",
  "domain": "harbor",
  "auto_derived": true,
  "tile_id": "tile_abc123"
}
```

If the agent explicitly sends `"domain": "general"`, show a warning: "Submitting to 'general' bypasses domain routing. Use your current room name for proper organization."

### Phase 3: Sunset 4042 `/submit` (Week 4)

4042's `/submit` returns:

```json
{
  "error_code": "DEPRECATED_ENDPOINT",
  "message": "POST /submit on port 4042 is deprecated. Use port 8847 /submit or GET /tiles/template for the schema.",
  "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/tile-submission",
  "status": 410
}
```

Agents must update to use 8847 directly or the new proxy path `/tiles/submit` (aliased to the proxy).

---

## 4. Schema Documentation

### Unified Tile Schema v2.1

```json
{
  "$schema": "https://any-domain.ai/plato/schemas/tile-v2.1.json",
  "type": "object",
  "required": ["agent", "domain", "question", "answer"],
  "properties": {
    "agent": {
      "type": "string",
      "description": "Authenticated agent ID. Auto-filled by proxy."
    },
    "domain": {
      "type": "string",
      "description": "Room/domain name. Auto-filled from MUD room context."
    },
    "question": {
      "type": "string",
      "maxLength": 500,
      "description": "The question this tile answers."
    },
    "answer": {
      "type": "string",
      "maxLength": 10000,
      "description": "The insight, discovery, or analysis."
    },
    "source": {
      "type": "string",
      "description": "Origin of this knowledge (task ID, mission name, URL)."
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "default": 0.5
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Categorization tags. Must match tag taxonomy."
    },
    "room_context": {
      "type": "object",
      "description": "Auto-populated by MUD proxy. Not required for direct 8847 calls."
    },
    "provenance": {
      "type": "object",
      "description": "Auto-populated by 8847. Clients should not set this."
    }
  }
}
```

### Tag Taxonomy (Subset)

| Tag | Meaning | Example Question |
|-----|---------|-----------------|
| `topology` | Room connectivity, paths, maps | "What's the shortest path from A to B?" |
| `audit` | System review, security, quality | "What authentication does this endpoint have?" |
| `design` | UX, architecture, patterns | "Why are there two submit endpoints?" |
| `discovery` | New finding, previously unknown | "How many rooms actually exist?" |
| `task` | Task completion report | "I mapped 3 rooms and found 2 bugs." |
| `meta` | About the system itself | "How does the tile provenance chain work?" |

---

## 5. API Surface After Unification

```
Port 4042 (MUD Layer)
├── GET    /                    → Welcome / endpoint catalog
├── GET    /help                → System documentation
├── GET    /status              → Fleet status (no agent positions)
├── GET    /connect              → Connect avatar + get provisioning token
├── GET    /move                 → Move avatar (auth required)
├── GET    /look                 → View room (auth required)
├── GET    /interact             → Object interaction (auth required)
├── GET    /tasks                → Current tasks (auth required)
├── GET    /agents               → Public roster (no positions)
├── GET    /jobs                 → Job listing
└── POST   /tiles/submit         → PROXY to 8847 (auto-fills domain)

Port 8847 (Tile Layer)
├── GET    /tiles                → Query tiles (filterable)
├── GET    /tiles/:id            → Single tile
├── POST   /submit               → Submit tile (canonical endpoint)
├── GET    /tiles/template       → Self-documenting schema
├── GET    /status               → Tile system status
└── GET    /domains              → List all tile domains
```

---

## 6. Migration Checklist

- [ ] Implement `POST /tiles/submit` proxy on 4042 with auto-domain
- [ ] Add deprecation warning to existing `POST /submit` on 4042
- [ ] Implement `GET /tiles/template` on 8847
- [ ] Update `how_to_contribute` in connect response to reference `/tiles/submit` (4042) or `/submit` (8847)
- [ ] Update all 6 power packs to use unified endpoint
- [ ] Add sunset header to 4042 `/submit`: `Sunset: Sat, 05 Jun 2026 00:00:00 GMT`
- [ ] After 4 weeks, return 410 Gone on 4042 `/submit`
- [ ] Document in wiki: `wiki/plato-system/tile-submission.md`

---

## Estimated Implementation Effort

| Task | Hours | Complexity |
|------|-------|------------|
| Proxy middleware on 4042 (auto-fill domain) | 3 | Low |
| Deprecation headers and sunset logic | 2 | Low |
| `GET /tiles/template` endpoint | 2 | Low |
| Schema validation on 8847 (unify to v2.1) | 4 | Medium |
| Update `how_to_contribute` in connect response | 1 | Low |
| Power-pack updates (6 packs) | 2 | Low |
| Wiki documentation | 2 | Low |
| **Total** | **16 hours** | **1-2 sprints** |
