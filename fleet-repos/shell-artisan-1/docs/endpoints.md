# PLATO Shell API Documentation

**Version:** v1.0  
**Base URL:** `http://147.224.38.131:8848`

---

## GET Endpoints

### `GET /`
Service metadata. Returns available endpoints and tools.

**Response:**
```json
{
  "service": "PLATO Shell v1.0 — The Agentic IDE",
  "endpoints": { "GET": {...}, "POST": {...} },
  "tools": ["shell", "kimi", "aider", "crush", "git", "test", "build", "review"],
  "rooms": ["harbor", "forge", ...]
}
```

### `GET /status`
Full admin view. Agents, rooms, recent commands, totals.

**Response:**
```json
{
  "agents": { "agent-name": { "room": "...", "connected_for": 800 } },
  "rooms": { "room-name": { "cwd": "...", "agents": [...], "command_count": 15 } },
  "total_commands": 23,
  "recent_commands": [...]
}
```

### `GET /feed?since=TIMESTAMP`
Global command feed since a Unix timestamp.

### `GET /rooms`
All rooms with execution contexts (CWD, branch, agents, commands).

### `GET /room/output?room=NAME&n=50`
Recent output for a specific room. `n` defaults to 50.

### `GET /admin`
Admin view (same as /status but potentially with extra admin-only fields).

### `GET /connect?agent=NAME&room=NAME`
Connect an agent to a room. Agent must exist.

### `GET /move?agent=NAME&room=NAME`
Move an agent to a different room.

---

## POST Endpoints

### `POST /cmd`
Execute a command.

**Body:**
```json
{
  "agent": "agent-name",
  "tool": "shell",
  "command": "ls -la",
  "timeout": 30
}
```

**Response:**
```json
{
  "id": "cmd-id",
  "agent": "agent-name",
  "room": "harbor",
  "tool": "shell",
  "command": "ls -la",
  "status": "completed",
  "output": "...",
  "error": "",
  "returncode": 0,
  "duration": 0.5
}
```

### `POST /cmd/kimi`
kimi-cli shortcut. Body same as `/cmd` but tool preset to `kimi`.

### `POST /cmd/aider`
aider shortcut. Body same as `/cmd` but tool preset to `aider`.

### `POST /cmd/shell`
Raw shell shortcut. Body same as `/cmd` but tool preset to `shell`.

### `POST /cmd/git`
git shortcut. Body same as `/cmd` but tool preset to `git`.

---

## Rooms

| Room | CWD | Purpose |
|------|-----|---------|
| harbor | /home/ubuntu/.openclaw/workspace | Main workspace |
| forge | /home/ubuntu/.openclaw/workspace/repos | Repository forge |
| tide-pool | /home/ubuntu/.openclaw/workspace | Shared workspace |
| lighthouse | /home/ubuntu/.openclaw/workspace | Monitoring / logs |
| dojo | /home/ubuntu/.openclaw/workspace/scripts | Training scripts |
| arena | /home/ubuntu/.openclaw/workspace | Combat / ELO system |
| ouroboros | /home/ubuntu/.openclaw/workspace | Grammar engine |
| engine-room | /home/ubuntu/.openclaw/workspace | Infrastructure |
| nexus | /home/ubuntu/.openclaw/workspace | Federation hub |
| research | /home/ubuntu/.openclaw/workspace/research | R&D |

---

## Tools

| Tool | Description | Safety Level |
|------|-------------|--------------|
| shell | Raw shell execution | ⚠️ Guarded |
| kimi | kimi-cli shortcut | ✅ Safe |
| aider | aider shortcut | ✅ Safe |
| crush | Unknown — investigate | 🛑 Unknown |
| git | git shortcut | ⚠️ Guarded |
| test | test runner | ✅ Safe |
| build | build system | ⚠️ Guarded |
| review | code review | ✅ Safe |

---

## Error Handling

- `400` — Bad request (missing params)
- `404` — Endpoint not found
- `500` — Command execution failed

Command failures are returned in the response body with `status: "failed"`, `error` field, and `returncode`.

---

## Notes for Agent Developers

1. **Always connect before executing** — Use `/connect` to ensure your agent is in the right room.
2. **Respect CWD** — Each room has its own working directory. `harbor` ≠ `dojo`.
3. **Use timeouts** — Default is 30s. Long-running commands need longer.
4. **Check returncode** — `0` = success, anything else = investigate.
5. **Read output before writing** — The shell-artisan-1 safety policy applies.
