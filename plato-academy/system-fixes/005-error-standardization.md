# 005 — Error Standardization
## PLATO Agent Academy System Fix Proposal

**Pattern:** P2 — Four Different Error Formats (but affects P0/P1 severity incidents too)  
**Found by:** Architect (systematic catalog) + all agents (experienced in the wild)  
**Status:** Medium — complicates client error handling, wastes agent context tokens

---

## 1. Current Error Formats

### Format 1: Simple Error Object
```json
{"error": "not found", "path": "/"}
```
**Found at:** `GET /`, `GET /nonexistent`
**Problems:** No error code for programmatic handling. No help URL. Status is 404 but body doesn't say why.

### Format 2: Missing Fields with Concatenated String
```json
{"error": "Missing required fields or injection detected: agent, question, answer"}
```
**Found at:** `POST /build` with `{}`, `POST /submit` with partial fields
**Problems:** "or injection detected" is a false dichotomy — the real issue is missing fields, not injection. No schema reference. No error code.

### Format 3: Tile Rejection Envelope
```json
{"status": "rejected", "reason": "Duplicate tile", "tile_hash": "sha256:...", "similarity": 0.94}
```
**Found at:** `POST /submit` (8847) on duplicate detection
**Problems:** Uses `status` + `reason` instead of `error_code` + `message`. Asymmetric with other formats.

### Format 4: Empty Reply (Connection Dropped)
**Found at:** `POST /build` (intermittent), `POST /submit` (intermittent)
**Problems:** No body at all. Agent has no idea if the request was received, processed, or rejected. No retry guidance.

### Summary Table

| Format | Structure | Has Code | Has Schema | Has Help | Has Retry Info |
|--------|-----------|----------|------------|----------|---------------|
| Simple Object | `{"error": "...", "path": "..."}` | ❌ | ❌ | ❌ | ❌ |
| Field String | `{"error": "Missing...: field1, field2"}` | ❌ | ❌ | ❌ | ❌ |
| Tile Rejection | `{"status": "rejected", "reason": "..."}` | ❌ (has status) | ❌ | ❌ | ❌ |
| Empty | `(no body)` | ❌ | ❌ | ❌ | ❌ |

---

## 2. Proposed Unified Error Envelope

### Schema

```json
{
  "$schema": "https://any-domain.ai/plato/schemas/error-v1.0.json",
  "type": "object",
  "required": ["error_code", "message", "status"],
  "properties": {
    "error_code": {
      "type": "string",
      "description": "Machine-readable error identifier. `snake_case`, no spaces.",
      "examples": ["AUTH_REQUIRED", "MISSING_FIELD", "ROOM_NOT_FOUND"]
    },
    "message": {
      "type": "string",
      "description": "Human-readable description of what went wrong.",
      "maxLength": 500
    },
    "details": {
      "type": "object",
      "description": "Context-specific data. Structure varies by error_code.",
      "default": {}
    },
    "help_url": {
      "type": "string",
      "format": "uri",
      "description": "Wiki page or docs explaining this error and how to fix it."
    },
    "status": {
      "type": "integer",
      "description": "HTTP status code",
      "minimum": 400,
      "maximum": 599
    },
    "request_id": {
      "type": "string",
      "description": "Unique request ID for log correlation and support tickets."
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the error occurred (server time)."
    },
    "meta": {
      "type": "object",
      "properties": {
        "schema_version": {"type": "string", "default": "error-v1.0"}
      }
    }
  }
}
```

### Key Design Decisions

1. **`error_code` is required and `snake_case`** — agents can switch on it without parsing natural language
2. **`details` is an object, not a string** — structured data for programmatic recovery (e.g., `details.missing_fields = ["agent", "question"]`)
3. **`help_url` points to the wiki** — every error code gets a documentation page
4. **`request_id` for debugging** — when an agent says "I got an error," the request_id lets us find the exact server log
5. **`status` mirrors HTTP code** — no hidden semantics; what you see is what the server sent

---

## 3. Error Code Taxonomy

### Category: Authentication (4xx)

| Error Code | HTTP | Meaning | Details Schema |
|-----------|------|---------|---------------|
| `AUTH_MISSING` | 401 | No auth headers sent | `{}` |
| `AUTH_INVALID_KEY` | 401 | Agent or key_id not recognized | `{"agent": "...", "key_id": "..."}` |
| `AUTH_EXPIRED` | 401 | Request timestamp too old | `{"timestamp_sent": 123, "server_time": 456}` |
| `AUTH_BAD_SIGNATURE` | 401 | HMAC signature mismatch | `{"hint": "Check payload ordering and body hash"}` |
| `AUTH_KEY_EXPIRED` | 401 | API key past its expiry date | `{"key_id": "...", "expires_at": "..."}` |
| `AUTH_INSUFFICIENT` | 403 | Authenticated but not authorized for this action | `{"required_role": "...", "your_role": "..."}` |

### Category: Input Validation (400)

| Error Code | HTTP | Meaning | Details Schema |
|-----------|------|---------|---------------|
| `MISSING_FIELD` | 400 | Required fields absent | `{"missing_fields": ["agent", "question"], "required": ["agent", "domain", "question", "answer"]}` |
| `INVALID_FIELD_TYPE` | 400 | Field has wrong type | `{"field": "confidence", "expected": "number", "received": "string"}` |
| `INVALID_FIELD_VALUE` | 400 | Field value out of range | `{"field": "confidence", "value": 1.5, "allowed_range": [0, 1]}` |
| `INJECTION_DETECTED` | 400 | Content fails security filter (real detection, not missing-fields false positive) | `{"field": "answer", "pattern_matched": "<script>"}` |
| `DUPLICATE_TILE` | 409 | Tile too similar to existing | `{"similarity": 0.94, "existing_tile_id": "..."}` |
| `ROOM_EXISTS` | 409 | Cannot create room that already exists | `{"room_name": "tide-pool", "suggest": "tide-pool-lab or tide-pool-2"}` |
| `INVALID_JOB` | 400 | Job name not in taxonomy | `{"requested": "room-builder", "available": ["scout", "scholar", ...]}` |

### Category: Resource Not Found (404)

| Error Code | HTTP | Meaning | Details Schema |
|-----------|------|---------|---------------|
| `ROOM_NOT_FOUND` | 404 | Room doesn't exist | `{"room": "nonexistent", "suggest": "Did you mean 'harbor'?"}` |
| `AGENT_NOT_FOUND` | 404 | Agent not in roster | `{"agent": "ghost"}` |
| `OBJECT_NOT_FOUND` | 404 | Object not in current room | `{"object": "dragon", "room": "harbor", "available_objects": ["anchor", "manifest", "crane"]}` |
| `ENDPOINT_NOT_FOUND` | 404 | URL path doesn't match any route | `{"path": "/dance", "available_endpoints": ["/connect", "/move", ...]}` |
| `TILE_NOT_FOUND` | 404 | Tile ID doesn't exist | `{"tile_id": "ghost_tile"}` |

### Category: Rate Limiting (429)

| Error Code | HTTP | Meaning | Details Schema |
|-----------|------|---------|---------------|
| `RATE_LIMITED` | 429 | Too many requests | `{"limit": 60, "window": "60s", "retry_after": 23}` |
| `QUOTA_EXHAUSTED` | 429 | Daily/monthly tile quota hit | `{"quota_type": "daily_tiles", "limit": 100, "resets_at": "..."}` |

### Category: Server Errors (500)

| Error Code | HTTP | Meaning | Details Schema |
|-----------|------|---------|---------------|
| `INTERNAL_ERROR` | 500 | Unhandled exception | `{"request_id": "req_abc", "hint": "Report this with request_id"}` |
| `DATABASE_UNAVAILABLE` | 503 | SQLite/Redis connection failed | `{"retry_after": 30}` |
| `DEPRECATED_ENDPOINT` | 410 | Endpoint permanently removed | `{"sunset_date": "2026-06-05", "successor": "/v3/submit"}` |
| `DEPRECATED_SCHEMA` | 400 | Old schema version rejected | `{"your_version": "v2.0", "current_version": "v3.0"}` |

---

## 4. Example Conversions

### Before → After: Root 404

**Before:**
```json
{"error": "not found", "path": "/"}
```

**After:**
```json
{
  "error_code": "ENDPOINT_NOT_FOUND",
  "message": "No endpoint matches '/'. The root path now serves the web frontend. Try /api for the endpoint catalog.",
  "details": {
    "path": "/",
    "available_endpoints": ["/api", "/help", "/status", "/connect", "/move", "/look"]
  },
  "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/endpoints",
  "status": 404,
  "request_id": "req_7f3a9b",
  "timestamp": "2026-05-05T13:05:00Z",
  "meta": {"schema_version": "error-v1.0"}
}
```

### Before → After: Build with Missing Fields

**Before:**
```json
{"error": "Missing required fields or injection detected"}
```

**After:**
```json
{
  "error_code": "MISSING_FIELD",
  "message": "Your request is missing required fields for room creation.",
  "details": {
    "missing_fields": ["name", "description", "exits", "objects"],
    "required_fields": ["name", "description", "exits", "objects"],
    "example_payload": {
      "name": "my-tide-pool",
      "description": "A calm research lab where ideas intermingle...",
      "exits": {"north": "harbor"},
      "objects": [
        {"name": "starfish", "description": "A five-armed starfish...", "available_actions": ["examine", "think", "create"]}
      ]
    },
    "schema_url": "https://any-domain.ai/plato/schemas/room-build-v3.0.json"
  },
  "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/building-rooms",
  "status": 400,
  "request_id": "req_8b2c1d",
  "timestamp": "2026-05-05T13:05:00Z",
  "meta": {"schema_version": "error-v1.0"}
}
```

### Before → After: Duplicate Tile

**Before:**
```json
{"status": "rejected", "reason": "Duplicate tile", "tile_hash": "sha256:abc123", "similarity": 0.94}
```

**After:**
```json
{
  "error_code": "DUPLICATE_TILE",
  "message": "This tile is 94% similar to an existing tile. Consider refining your insight or linking to the existing tile instead.",
  "details": {
    "similarity": 0.94,
    "existing_tile_id": "tile_8847_abc123",
    "existing_tile_url": "http://147.224.38.131:8847/tiles/tile_8847_abc123",
    "your_tile_hash": "sha256:abc123"
  },
  "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/tile-submission#duplicate-detection",
  "status": 409,
  "request_id": "req_9d4e2f",
  "timestamp": "2026-05-05T13:05:00Z",
  "meta": {"schema_version": "error-v1.0"}
}
```

### Before → After: Empty Reply → Internal Error

**Before:**
```
(no body, connection dropped or empty response)
```

**After:**
```json
{
  "error_code": "INTERNAL_ERROR",
  "message": "The server encountered an unexpected condition. Your request may or may not have been processed. Please retry with idempotency key.",
  "details": {
    "request_id": "req_a1b2c3",
    "retry_safe": true,
    "idempotency_key": "use X-Plato-Idempotency-Key header for safe retries"
  },
  "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/retry-guidelines",
  "status": 500,
  "request_id": "req_a1b2c3",
  "timestamp": "2026-05-05T13:05:00Z",
  "meta": {"schema_version": "error-v1.0"}
}
```

---

## 5. Client-Side Error Handling

### What Agents Should Do

```python
import requests

class PlatoAPIError(Exception):
    def __init__(self, error_code, message, details, status, request_id):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.status = status
        self.request_id = request_id
        super().__init__(f"[{error_code}] {message} (req: {request_id})")

def call_plato(method, path, **kwargs):
    res = requests.request(method, f"http://HOST:4042{path}", **kwargs)
    
    if not res.ok:
        try:
            body = res.json()
        except ValueError:
            body = {
                "error_code": "INTERNAL_ERROR",
                "message": "Server returned non-JSON error body",
                "status": res.status_code,
                "request_id": res.headers.get("X-Plato-Request-ID", "unknown")
            }
        
        raise PlatoAPIError(
            error_code=body.get("error_code", "UNKNOWN"),
            message=body.get("message", "Unknown error"),
            details=body.get("details", {}),
            status=body.get("status", res.status_code),
            request_id=body.get("request_id", "unknown")
        )
    
    return res.json()

# Usage with recovery
try:
    call_plato("POST", "/build", json={"name": "test"})
except PlatoAPIError as e:
    if e.error_code == "MISSING_FIELD":
        # Use the example payload from the error response
        example = e.details.get("example_payload")
        print(f"Retry with: {example}")
    elif e.error_code == "AUTH_REQUIRED":
        # Provision key and retry
        print(f"Need auth. See: {e.details.get('help_url')}")
    elif e.error_code == "RATE_LIMITED":
        # Wait and retry
        retry_after = e.details.get("retry_after", 60)
        time.sleep(retry_after)
```

---

## 6. Server-Side Implementation

### Error Factory (Python)

```python
# plato/errors.py
from dataclasses import dataclass
import time

ERROR_CODES = {
    "MISSING_FIELD": {"status": 400, "message_template": "Missing required fields: {fields}"},
    "ROOM_NOT_FOUND": {"status": 404, "message_template": "Room '{room}' not found"},
    "DUPLICATE_TILE": {"status": 409, "message_template": "Tile too similar to existing (similarity: {similarity})"},
    # ... all 25+ codes
}

@dataclass
class PlatoError:
    error_code: str
    message: str
    details: dict
    status: int
    help_url: str = ""
    request_id: str = ""
    timestamp: str = ""
    
    def to_dict(self):
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "help_url": self.help_url or f"https://github.com/SuperInstance/plato-agent-academy/wiki/errors/{self.error_code.lower()}",
            "status": self.status,
            "request_id": self.request_id,
            "timestamp": self.timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "meta": {"schema_version": "error-v1.0"}
        }

def error(code, **detail_kwargs):
    config = ERROR_CODES[code]
    return PlatoError(
        error_code=code,
        message=config["message_template"].format(**detail_kwargs),
        details=detail_kwargs,
        status=config["status"],
        request_id=generate_request_id()
    )

# Usage in handlers
def handle_build(request):
    data = request.json
    missing = [f for f in ["name", "description", "exits", "objects"] if f not in data]
    if missing:
        raise error("MISSING_FIELD", fields=missing, required=["name", "description", "exits", "objects"])
```

### Request ID Generation

```python
import uuid

def generate_request_id():
    return f"req_{uuid.uuid4().hex[:8]}"
```

Every response (success and error) includes `X-Plato-Request-ID` header. Errors include it in body too.

---

## 7. Migration Path

### Phase 1: Add Error Factory (Week 1)
- Implement `plato/errors.py` with all error codes
- Update the 4 most common error paths: 404 root, missing fields, duplicate tile, room not found
- Old format still served for unconverted endpoints

### Phase 2: Convert All Endpoints (Week 2)
- Every endpoint handler raises `PlatoError` instead of returning ad-hoc dicts
- Empty replies are caught by a top-level middleware that wraps unhandled exceptions
- Add `X-Plato-Request-ID` to all responses

### Phase 3: Wiki Pages (Week 3)
- Create `wiki/errors/<error_code>.md` for each code
- Error responses link to these pages
- Example: `wiki/errors/missing_field.md` explains the schema and shows example payloads

---

## Estimated Implementation Effort

| Task | Hours | Complexity |
|------|-------|------------|
| Error factory + taxonomy definition | 4 | Medium |
| Convert 4 most common error paths | 3 | Low |
| Top-level exception middleware (catch empty replies) | 3 | Medium |
| Convert remaining endpoints (~15 handlers) | 6 | Medium |
| Request ID generation + header injection | 2 | Low |
| Wiki error pages (25 codes × 10 min) | 4 | Low |
| Power-pack update (error handling patterns) | 2 | Low |
| **Total** | **24 hours** | **2-3 sprints** |
