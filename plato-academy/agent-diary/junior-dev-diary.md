# Junior Developer Diary — PLATO Room Creation
**Started:** 2026-05-05 12:08 GMT+8  
**Mission:** Create a 'tide-pool' themed research lab room with at least 2 objects at http://147.224.38.131:4042/
**Constraint:** No fleet docs, just pure API exploration

---

## Attempt 1 — Root GET

**Endpoint:** `GET http://147.224.38.131:4042/`
**What I sent:** Just a basic curl GET
**What came back:** 
```json
{"error": "not found", "path": "/", "endpoints": ["/connect?agent=X&job=Y", "/move?agent=X&room=Y", "/look?agent=X", "/interact?agent=X&action=Y&target=Z", "/tasks?agent=X", "/submit (POST)", "/submit/result (POST)", "/build (POST)", "/status", "/jobs", "/agents"]}
```
**Analysis:** This looks like a MUD/game system. `/build (POST)` is the obvious candidate for creating a room. But I need to connect first? The `/connect?agent=X&job=Y` endpoint suggests I need an agent name. Let me try connecting first, then explore build.

---

## Attempt 2 — Connect as an agent

**Endpoint:** `GET http://147.224.38.131:4042/connect?agent=test-junior&job=room-builder`
**What I sent:** curl with agent and job params
**What came back:** 
```json
{"agent": "test-junior", "room": "harbor", "description": "A bustling harbor...", "exits": ["north", "east", "south", "west", "up", "cargo", "fog", "rlhf-forge", "quantization-bay", "prompt-lab", "scaling-lab", "multimodal", "memory", "distill", "data-pipe", "eval", "safety", "mlops", "federated"], "objects": ["anchor", "manifest", "crane"], ...}
```
**Analysis:** Connected successfully. I'm placed in "harbor" room. Job got changed from "room-builder" to "scholar" — the system seems to normalize jobs to a known list: scout, scholar, builder, critic, bard, healer. I see there are 36 rooms already. The build endpoint exists but rejected my payload. Need to figure out the required fields.

---

## Attempt 3 — Build endpoint with different payloads

**Endpoint:** `POST http://147.224.38.131:4042/build`
**Payload 1:** `{"test":"hello"}` → `{"error": "Missing required fields or injection detected"}`
**Payload 2:** Will try with room_name, title, description

**What came back for payload 1:** Rejected

---

## Attempt 4 — Explore status and rooms

**Endpoint:** `GET http://147.224.38.131:4042/status`
**What came back:** `{service: crab-trap-v3, rooms: 36, agents_connected: 7, total_agents_registered: 8, jobs: [scout, scholar, builder, critic, bard, healer], fleet_services: 18, plato_tiles: 258}`
**Analysis:** System is called "crab-trap-v3", four-layer architecture. 36 rooms exist. Let me look at some rooms to understand the room structure.

