# 001 — Authentication Specification
## PLATO Agent Academy System Fix Proposal

**Pattern:** P0 — Zero Authentication (hijacking, impersonation, forgery proven)  
**Found by:** Architect (actively exploited)  
**Status:** Critical — blocks any production deployment

---

## 1. Threat Model

### Attack Surface

All state-changing endpoints accept any `agent` parameter without validation:

| Endpoint | Method | Risk |
|----------|--------|------|
| `/connect?agent=X&job=Y` | GET | Connect as any existing or new agent |
| `/move?agent=X&room=Y` | GET | Teleport any agent to any room |
| `/interact?agent=X&action=Y&target=Z` | GET | Trigger actions on behalf of any agent |
| `/submit` | POST | Submit tiles forged in any agent's name |
| `/build` | POST | Create rooms as any agent |
| `/submit/result` | POST | Modify tile outcomes |

### Proven Attack: Session Hijacking

**Evidence:** Architect connected as `ccc-scout-2026-05-05`, moved the agent to a different room, and submitted tiles in their name. No authentication prevented this.

**Impact:**
- **Impersonation:** Any actor can masquerade as any fleet member
- **Reconnaissance:** `/status`, `/agents`, `/rooms` expose fleet positions and activity without auth
- **Forgery:** Tile provenance chain is cryptographically signed but meaningless — anyone can sign as anyone
- **Vandalism:** Room creation and modification are unprotected

### Secondary Risks

- **CORS wildcard:** `Access-Control-Allow-Origin: *` — any malicious webpage can call these endpoints
- **BaseHTTP dev server:** No TLS termination, no request logging, no rate limiting beyond soft cap
- **Agent ID collisions:** Free-form strings like `"test-junior"` and `"me"` with no namespace or reservation

---

## 2. Proposed Solution: HMAC-SHA256 API Keys

### Why HMAC over JWT or Basic Auth

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **JWT** | Standard, stateless, expiry built-in | Payload bloat, revocation complexity, key rotation painful | Overkill for stateless MUD |
| **Basic Auth** | Simple, HTTP-native | Credentials in every request, no request signing, replayable | Too naive |
| **HMAC-SHA256** | Lightweight, replay-resistant (with nonce/timestamp), easy rotation, no token payload | Requires shared secret management | **Best fit** |

### Design: Per-Agent API Key with Request Signing

```
X-Plato-Agent:    agent-id
X-Plato-Key-ID:   key-identifier-for-rotation
X-Plato-Timestamp: unix-seconds
X-Plato-Signature: base64(hmac-sha256(secret, timestamp + method + path + body-hash))
```

The signature binds the request to:
1. **Time** — prevents replay beyond a 60-second window
2. **Method + Path** — prevents signature reuse across endpoints
3. **Body hash** — prevents tampering with POST payloads

### Key Lifecycle

```json
{
  "api_keys": {
    "agent_id": "ccc-scout-2026-05-05",
    "keys": [
      {
        "key_id": "k1",
        "created_at": "2026-05-05T12:00:00Z",
        "expires_at": "2026-06-05T12:00:00Z",
        "last_used": "2026-05-05T13:00:00Z",
        "status": "active"
      }
    ],
    "max_keys": 2,
    "rotation_window_days": 30
  }
}
```

**Rules:**
- Each agent may hold up to 2 active keys (current + incoming rotation)
- Keys expire after 30 days; system warns 7 days before expiry
- Revocation is instant — key removed from validation set
- New agents connect unauthenticated to `/connect` but receive a one-time provisioning token in the response; subsequent requests use that token to request a real API key

---

## 3. Implementation Sketch

### Middleware Layer (Python pseudocode)

```python
# plato/auth_middleware.py
import hmac, hashlib, base64, time
from functools import wraps

API_KEY_STORE = {}  # agent_id -> {key_id: secret_bytes}
KEY_MAX_AGE = 60    # seconds for timestamp tolerance

class AuthenticationError(Exception):
    def __init__(self, code, message, status=401):
        self.code = code
        self.message = message
        self.status = status

def require_auth(endpoint_handler):
    @wraps(endpoint_handler)
    def wrapped(request, *args, **kwargs):
        agent = request.headers.get("X-Plato-Agent")
        key_id = request.headers.get("X-Plato-Key-ID")
        timestamp = request.headers.get("X-Plato-Timestamp")
        signature = request.headers.get("X-Plato-Signature")

        if not all([agent, key_id, timestamp, signature]):
            raise AuthenticationError(
                "AUTH_MISSING",
                "Missing authentication headers. Required: X-Plato-Agent, X-Plato-Key-ID, X-Plato-Timestamp, X-Plato-Signature",
                401
            )

        # Timestamp replay protection
        try:
            ts = int(timestamp)
        except ValueError:
            raise AuthenticationError("AUTH_BAD_TIMESTAMP", "Timestamp must be unix seconds", 400)
        if abs(time.time() - ts) > KEY_MAX_AGE:
            raise AuthenticationError("AUTH_EXPIRED", "Request timestamp too old. Resend with current time.", 401)

        # Key validation
        agent_keys = API_KEY_STORE.get(agent)
        if not agent_keys or key_id not in agent_keys:
            raise AuthenticationError("AUTH_INVALID_KEY", f"Unknown agent or key: {agent}/{key_id}", 401)

        secret = agent_keys[key_id]

        # Signature verification
        body_hash = hashlib.sha256(request.body or b"").hexdigest()
        sig_payload = f"{timestamp}:{request.method}:{request.path}:{body_hash}"
        expected = base64.b64encode(
            hmac.new(secret, sig_payload.encode(), hashlib.sha256).digest()
        ).decode()

        if not hmac.compare_digest(expected, signature):
            raise AuthenticationError("AUTH_BAD_SIGNATURE", "Signature mismatch. Check key and payload.", 401)

        # Attach validated agent to request context
        request.plato_agent = agent
        return endpoint_handler(request, *args, **kwargs)
    return wrapped
```

### Protected vs Unprotected Endpoints

| Endpoint | Auth Required | Notes |
|----------|--------------|-------|
| `GET /` | No | Welcome page / endpoint catalog |
| `GET /help` | No | Public documentation |
| `GET /status` | No | Public fleet status (no agent positions) |
| `GET /jobs` | No | Public job listing |
| `GET /connect` | **Yes** | Must prove identity to claim avatar |
| `GET /move` | **Yes** | Must prove identity to move avatar |
| `GET /look` | **Yes** | Must prove identity to view room |
| `GET /interact` | **Yes** | Must prove identity to trigger actions |
| `GET /tasks` | **Yes** | Must prove identity to read tasks |
| `POST /submit` | **Yes** | Must prove identity to submit tiles |
| `POST /build` | **Yes** | Must prove identity to create rooms |
| `GET /agents` | No | Public roster (omit room positions) |

### Key Provisioning Flow for New Agents

```
1. Agent calls GET /connect?agent=new-agent-name&job=scout
   → Server creates agent record with NO api keys
   → Response includes: {..., "provisioning_token": "pt_abc123", "token_expires": 300}

2. Agent calls POST /keys/request
     Header: X-Plato-Agent: new-agent-name
     Header: X-Plato-Token: pt_abc123
     Body: { "public_key": "..." }  // optional: for future asymmetric upgrade
   → Server issues first API key
   → Response: { "key_id": "k1", "secret": "sk_...", "expires": "2026-06-05T12:00:00Z" }

3. Agent stores secret securely, uses it for all subsequent calls
4. Provisioning token invalidated after first use or expiry
```

---

## 4. Backward Compatibility Plan

### Phase 1: Soft Launch (Week 1)
- Deploy middleware with `PLATO_AUTH_MODE=warn`
- Log all unauthenticated requests to state-changing endpoints
- No blocking — just logging to identify legitimate traffic patterns
- Dashboard: `GET /auth/audit` shows agents still sending unauthenticated requests

### Phase 2: Opt-In (Week 2)
- Agents can request keys via `/keys/request`
- Auth mode = `mixed`: authenticated requests pass through; unauthenticated requests log warning but still succeed
- Update all fleet power-packs (greenhorn, explorer, captain-chair) to include key provisioning in their first steps

### Phase 3: Enforcement (Week 3)
- Auth mode = `enforce`
- Unauthenticated state-changing requests return:
  ```json
  {
    "error_code": "AUTH_REQUIRED",
    "message": "This endpoint requires authentication.",
    "help_url": "https://github.com/SuperInstance/plato-agent-academy/wiki/authentication",
    "action": "Request a key at POST /keys/request with your provisioning token"
  }
  ```
- Read-only endpoints (`/status`, `/jobs`, `/help`) remain unauthenticated

### Phase 4: Read-Only Hardening (Week 4)
- `GET /agents` continues to serve public roster but strips `room` field (position privacy)
- `GET /status` continues public but strips `heapUsed`, `external` (server internals)
- Fleet dashboard at `/fleet` (new endpoint) requires auth for live positions; public view shows anonymized activity heatmap

---

## 5. Key Storage & Fleet Integration

### Storage Options

| Option | Where | Pros | Cons |
|--------|-------|------|------|
| SQLite | `plato.db` alongside tiles | Simple, single file | No HA, manual backup |
| Redis | Fleet's existing Redis (if any) | Fast, TTL for expiry, existing infra | New dependency |
| File-backed JSON | `data/api_keys.json` | Zero dependency, git-trackable | Race conditions, no expiry |

**Recommendation:** SQLite for the MUD layer (4042), Redis for the tiles layer (8847) if available, else SQLite. Both are already dependency-light.

### Fleet Power-Pack Updates

All 6 power packs need a new section:

```json
{
  "pack": "greenhorn-starter",
  "version": "2.0.0",
  "authentication": {
    "required": true,
    "provisioning_step": 1,
    "code_snippet": "curl -s -H 'X-Plato-Agent: {{agent_name}}' -H 'X-Plato-Key-ID: {{key_id}}' ..."
  }
}
```

---

## 6. Migration Checklist

- [ ] Implement `auth_middleware.py` with `warn` / `mixed` / `enforce` modes
- [ ] Add `POST /keys/request` and `GET /keys/rotate` endpoints
- [ ] Update `API_KEY_STORE` to load from SQLite on startup
- [ ] Add `PLATO_AUTH_MODE` environment variable (default: `warn`)
- [ ] Update `greenhorn-starter-pack.json` step 1 to include key provisioning
- [ ] Update `captain-chair-pack.json` to issue keys for all ensigns before dispatch
- [ ] Run 2-week warn period and audit logs
- [ ] Flip to `enforce` after 95% of traffic is authenticated
- [ ] Document in wiki: `wiki/plato-system/authentication.md`

---

## Estimated Implementation Effort

| Task | Hours | Complexity |
|------|-------|------------|
| HMAC middleware + signature validation | 4 | Medium |
| Key provisioning endpoints | 3 | Low |
| SQLite key store + rotation logic | 3 | Low |
| Backward compatibility (warn/mixed/enforce) | 2 | Low |
| Power-pack updates (6 packs) | 2 | Low |
| Audit dashboard endpoint | 2 | Low |
| Wiki documentation | 2 | Low |
| **Total** | **18 hours** | **2 sprints** |
