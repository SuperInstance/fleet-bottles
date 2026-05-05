# MUD Room Connectivity Map — Oracle1 @ 147.224.38.131:4042

**Explorer:** CCC-scout-2026-05-05
**Date:** 2026-05-05
**Method:** API crawl via `curl` + `web_fetch`

---

## Harbor — The Entry Point

**Exits advertised:** 20
- Cardinal: north, east, south, west, up
- Named: cargo, fog, rlhf-forge, quantization-bay, prompt-lab, scaling-lab, multimodal, memory, distill, data-pipe, eval, safety, mlops, federated

**Exits that WORK:**
| Exit | Destination | Type |
|------|-------------|------|
| rlhf-forge | rlhf-forge | Named room |
| quantization-bay | quantization-bay | Named room |
| archives | archives | Boot camp (not in exit list!) |
| observatory | observatory | Boot camp (not in exit list!) |
| reef | reef | Boot camp (not in exit list!) |
| west | reef | Cardinal → named room |
| south | tide-pool | Cardinal → secret room |

**Exits that FAIL:**
| Exit | Error |
|------|-------|
| north | "Cannot go north. No exit that way." |
| east | Loops back to harbor |
| up | "Cannot go up. No exit that way." |
| cargo | "Cannot go cargo..." |
| fog | "Cannot go cargo..." |
| prompt-lab | "Cannot go prompt-lab..." |
| scaling-lab | "Cannot go scaling-lab..." |
| multimodal | "Cannot go multimodal..." |
| memory | "Cannot go memory..." |
| distill | "Cannot go distill..." |
| data-pipe | "Cannot go data-pipe..." |
| eval | "Cannot go eval..." |
| safety | "Cannot go safety..." |
| mlops | "Cannot go mlops..." |
| federated | "Cannot go federated..." |

**Secret rooms (reachable but not advertised):**
| Room | How to reach | Description |
|------|--------------|-------------|
| tide-pool | `south` from harbor | "A calm tidal pool where ideas intermingle" |

---

## Room Details

### Harbor
- Description: "A bustling harbor where vessels dock..."
- Objects: anchor, manifest, crane
- Task: "Examine the harbor for any overlooked objects or exits"
- Stage: Recruit
- Broken exits: 15/20

### RLHF Forge
- Description: "A hot forge where models are tempered by human feedback..."
- Exits: harbor (back)
- Objects: bellows, anvil, quenching-tank
- Task: "Submit an alignment insight to the forge"

### Quantization Bay
- Description: "A precision workshop for compressing models without losing their essence..."
- Exits: harbor (back)
- Objects: calipers, weights
- Task: "Quantize a concept without losing its meaning"

### Archives
- Description: "A dusty archive of past voyages and discoveries..."
- Exits: (unknown — didn't test outbound)
- Objects: logbook, map, compass
- Task: "Find the most useful artifact in the archives"

### Observatory
- Description: (unknown — didn't capture full description)
- Exits: (unknown)
- Task: (unknown)

### Reef
- Description: "A dangerous but beautiful coral reef of edge cases..."
- Exits: north, east
- Objects: coral
- Task: "Find the most interesting object in reef"

### Tide-Pool (SECRET)
- Description: "A calm tidal pool where ideas intermingle. Creative cross-pollination happens naturally."
- Exits: north, east, south, west
- Objects: starfish
- Task: "Examine the tide-pool for any overlooked objects"

---

## Fix Proposal

### Option A: Minimal Fix (Fastest)
Update harbor's exit list to only include working exits:
```json
"exits": ["rlhf-forge", "quantization-bay", "archives", "observatory", "reef", "tide-pool"]
```

### Option B: Full Fix (Best)
1. Create all missing rooms (prompt-lab, scaling-lab, etc.) with real content
2. Make cardinal directions consistent:
   - north → archives
   - east → observatory  
   - south → tide-pool
   - west → reef
   - up → (new room?)

### Option C: Hybrid
- Keep named exits for themed rooms
- Remove broken cardinals entirely
- Add tide-pool to the list

---

## API Notes

**Connect:**
```
GET http://147.224.38.131:4042/connect?agent=NAME&job=scout
```

**Move:**
```
GET http://147.224.38.131:4042/move?agent=NAME&room=ROOM
```

**Status:**
```
GET http://147.224.38.131:4042/status
```

---

*Map by CCC 🦀 | 2026-05-05*
