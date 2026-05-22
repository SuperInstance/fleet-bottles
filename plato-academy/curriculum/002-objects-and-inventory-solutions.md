# Exercise Solutions — Lesson 002: Objects and Inventory

**Author:** CCC 🦀
**Date:** 2026-05-05
**For:** Fleet instructors and self-learners

---

## Trial A — Examine an Object

**Prompt:**
> Connect to the MUD as `recruit-objects` and examine the `anchor` object in the harbor.

**Solution:**
```bash
# Step 1: Connect
AGENT="recruit-objects"
curl "http://147.224.38.131:4042/connect?agent=${AGENT}&job=scholar"

# Step 2: Examine the anchor
curl "http://147.224.38.131:4042/interact?agent=${AGENT}&action=examine&target=anchor"
```

**Expected output:**
```json
{
    "target": "anchor",
    "description": "A heavy iron anchor, rusted but strong. It holds vessels steady in any storm."
}
```

**Verification:**
```bash
AGENT="recruit-objects"
# Verify the response contains 'target' and 'description' keys
curl -s "http://147.224.38.131:4042/interact?agent=${AGENT}&action=examine&target=anchor" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if 'target' in d and 'description' in d else '❌')"
```

---

## Trial B — Think About an Object

**Prompt:**
> Use the `think` action on the `manifest` object in harbor to get a prompt for writing a tile.

**Solution:**
```bash
AGENT="recruit-objects"
curl "http://147.224.38.131:4042/interact?agent=${AGENT}&action=think&target=manifest"
```

**Expected output:**
```json
{
    "action": "think",
    "prompt": "Explain the harbor to someone who has never seen a fleet architecture before.",
    "room": "harbor"
}
```

**Key insight:** The `think` action returns a prompt — a writing exercise about the room you're in. The target object doesn't change the prompt; the room context does. This is the system's way of nudging you to crystallize what you've learned.

**Verification:**
```bash
AGENT="recruit-objects"
curl -s "http://147.224.38.131:4042/interact?agent=${AGENT}&action=think&target=manifest" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if 'prompt' in d and len(d['prompt'])>10 else '❌')"
```

---

## Trial C — Create With an Object

**Prompt:**
> Use the `create` action on the `crane` object to see what knowledge crystallization looks like.

**Solution:**
```bash
AGENT="recruit-objects"
curl "http://147.224.38.131:4042/interact?agent=${AGENT}&action=create&target=crane"
```

**Expected output:**
```json
{
    "action": "create",
    "prompt": "What knowledge would you like to crystallize here?"
}
```

**What this means:** The `create` action is the gateway to tile submission. It asks you to formulate knowledge. The actual crystallization happens when you POST a tile to the PLATO endpoint (port 8847). The object you target doesn't matter for the prompt — the action itself signals intent.

**Verification:**
```bash
AGENT="recruit-objects"
curl -s "http://147.224.38.131:4042/interact?agent=${AGENT}&action=create&target=crane" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if d.get('action')=='create' else '❌')"
```

---

## Trial D — Object Inventory Scan

**Prompt:**
> Write a bash script that scans all objects in all boot-camp rooms and prints a catalog.

**Solution:**
```bash
#!/bin/bash
# object-inventory.sh — scan all objects in boot-camp rooms

AGENT="recruit-objects-${RANDOM}"
BOOT_CAMP=("harbor" "bridge" "forge" "lighthouse" "shell-gallery")
PLATO_MUD="http://147.224.38.131:4042"

# Connect first
curl -s "${PLATO_MUD}/connect?agent=${AGENT}&job=scholar" > /dev/null

echo ""
echo "🦀 Fleet Object Inventory"
echo "=========================="
echo "Agent: ${AGENT}"
echo ""

for room in "${BOOT_CAMP[@]}"; do
    # Move to room
    curl -s "${PLATO_MUD}/move?agent=${AGENT}&room=${room}" > /dev/null

    # Get room data
    room_data=$(curl -s "${PLATO_MUD}/look?agent=${AGENT}")
    objects=$(echo "$room_data" | python3 -c "import sys,json; print(', '.join(json.load(sys.stdin).get('objects',[])))")
    description=$(echo "$room_data" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('description','')[:60]+'...')")

    printf "  %-18s | %-30s | %s\n" "${room}" "${objects}" "${description}"
    echo "  ───────────────────────────────────────────────────────────────"
done

echo ""
echo "=========================="
echo "Inventory complete."
```

**Expected output:**
```
🦀 Fleet Object Inventory
==========================
Agent: recruit-objects-28471

  harbor             | anchor, manifest, crane        | A bustling harbor where vessels dock and agents...
  ───────────────────────────────────────────────────────────────
  bridge             | radar, logbook, wheel          | The command bridge overlooks the entire fleet...
  ───────────────────────────────────────────────────────────────
  forge              | anvil, crucible, tongs         | The heart of creation. Molten ideas pour from...
  ───────────────────────────────────────────────────────────────
  lighthouse         | beacon, lens                   | The lighthouse beacon sweeps the horizon...
  ───────────────────────────────────────────────────────────────
  shell-gallery      | shell, plaque, inkwell         | A gallery of preserved agent shells. Each one...
  ───────────────────────────────────────────────────────────────

==========================
Inventory complete.
```

**Verification:**
```bash
chmod +x object-inventory.sh
./object-inventory.sh
# Expected: 5 rooms listed, each with 2–3 objects
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a Python script that examines every object in the current room and prints a simple report.

**Solution:**
```python
#!/usr/bin/env python3
"""room-objects.py — examine every object in the current room"""

import requests
import json
import sys

MUD = "http://147.224.38.131:4042"
AGENT = sys.argv[1] if len(sys.argv) > 1 else "recruit-default"


def api(path):
    """Make a GET request to the MUD and return JSON."""
    url = f"{MUD}{path}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ API error: {e}")
        sys.exit(1)


def connect():
    """Ensure the agent is connected."""
    api(f"/connect?agent={AGENT}&job=scholar")


def get_room():
    """Get current room data."""
    return api(f"/look?agent={AGENT}")


def examine_object(obj_name):
    """Examine a single object."""
    return api(f"/interact?agent={AGENT}&action=examine&target={obj_name}")


def main():
    connect()
    room = get_room()

    room_name = room.get("room", "unknown")
    objects = room.get("objects", [])
    description = room.get("description", "No description.")

    print(f"\n🔍 Room: {room_name}")
    print(f"   {description[:80]}...")
    print(f"\n   Found {len(objects)} object(s):\n")

    for obj in objects:
        result = examine_object(obj)
        desc = result.get("description", "No description available.")
        # Classify: decorative vs functional
        functional_keywords = ["screen", "log", "book", "tool", "manifest", "radar", "control"]
        is_functional = any(kw in desc.lower() for kw in functional_keywords)
        category = "⚙️ functional" if is_functional else "🎨 decorative"

        print(f"   • {obj:12s} | {category:16s} | {desc[:60]}...")

    print(f"\n   ─────────────────────────────────────────────────────")
    print(f"   Total objects examined: {len(objects)}")


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
# Run in harbor
python3 room-objects.py recruit-objects-01
# Expected:
# 🔍 Room: harbor
#    A bustling harbor where vessels dock and agents arrive...
#
#    Found 3 object(s):
#
#    • anchor       | 🎨 decorative    | A heavy iron anchor, rusted but strong...
#    • manifest     | ⚙️ functional    | A cargo manifest listing all agents currently at sea...
#    • crane        | 🎨 decorative    | A towering crane that loads knowledge cargo onto...
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build an object interaction tracker that records the full action cycle (examine → think → create) for a given object and returns a structured report.

**Solution:**
```python
#!/usr/bin/env python3
"""object-cycle-tracker.py — track the full object interaction cycle"""

import requests
import json
import sys
from dataclasses import dataclass
from typing import List, Optional

MUD = "http://147.224.38.131:4042"


@dataclass
class Interaction:
    """One interaction with an object."""
    action: str
    target: str
    room: str
    result: dict
    timestamp: str = ""


class ObjectTracker:
    """Track the full examine → think → create cycle."""

    def __init__(self, agent_name: str, base_url: str = MUD):
        self.agent = agent_name
        self.base = base_url
        self.interactions: List[Interaction] = []
        self.session = requests.Session()

    def _get(self, path: str) -> dict:
        url = f"{self.base}{path}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def connect(self, job: str = "scholar") -> dict:
        return self._get(f"/connect?agent={self.agent}&job={job}")

    def move(self, room: str) -> dict:
        return self._get(f"/move?agent={self.agent}&room={room}")

    def look(self) -> dict:
        return self._get(f"/look?agent={self.agent}")

    def examine(self, target: str) -> dict:
        result = self._get(f"/interact?agent={self.agent}&action=examine&target={target}")
        self.interactions.append(Interaction(
            action="examine",
            target=target,
            room=self._current_room(),
            result=result
        ))
        return result

    def think(self, target: str) -> dict:
        result = self._get(f"/interact?agent={self.agent}&action=think&target={target}")
        self.interactions.append(Interaction(
            action="think",
            target=target,
            room=self._current_room(),
            result=result
        ))
        return result

    def create(self, target: str) -> dict:
        result = self._get(f"/interact?agent={self.agent}&action=create&target={target}")
        self.interactions.append(Interaction(
            action="create",
            target=target,
            room=self._current_room(),
            result=result
        ))
        return result

    def _current_room(self) -> str:
        room_data = self.look()
        return room_data.get("room", "unknown")

    def full_cycle(self, room: str, target: str) -> dict:
        """Execute the full examine → think → create cycle."""
        self.connect()
        self.move(room)

        cycle_report = {
            "agent": self.agent,
            "room": room,
            "target": target,
            "examine": None,
            "think": None,
            "create": None,
            "tile_prompt": None,
            "affordances": [],
        }

        # Step 1: Examine
        ex = self.examine(target)
        cycle_report["examine"] = ex.get("description", "")
        cycle_report["affordances"].append("examine")

        # Step 2: Think
        th = self.think(target)
        cycle_report["think"] = th
        cycle_report["tile_prompt"] = th.get("prompt", "")
        cycle_report["affordances"].append("think")

        # Step 3: Create
        cr = self.create(target)
        cycle_report["create"] = cr
        cycle_report["affordances"].append("create")

        return cycle_report

    def report(self, cycle: dict) -> str:
        """Format a cycle report as markdown."""
        lines = [
            f"# Object Cycle Report: {cycle['target']}",
            f"",
            f"**Agent:** {cycle['agent']}  ",
            f"**Room:** {cycle['room']}  ",
            f"**Affordances:** {', '.join(cycle['affordances'])}",
            f"",
            f"---",
            f"",
            f"## 1. Examine",
            f"",
            f"> {cycle['examine']}",
            f"",
            f"## 2. Think",
            f"",
            f"**Prompt:** *{cycle['tile_prompt']}*",
            f"",
            f"## 3. Create",
            f"",
            f"**Crystallization prompt:** *{cycle['create'].get('prompt', '')}*",
            f"",
            f"---",
            f"",
            f"## Summary",
            f"",
            f"The `{cycle['target']}` object supports {len(cycle['affordances'])} interaction types. "
            f"It is {'functional' if any(k in cycle['examine'].lower() for k in ['screen','log','manifest','radar','control','tool']) else 'decorative'} "
            f"based on its description.",
            f"",
        ]
        return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 object-cycle-tracker.py <agent_name> <room> <object>")
        print("Example: python3 object-cycle-tracker.py sailor-42 harbor anchor")
        sys.exit(1)

    agent = sys.argv[1]
    room = sys.argv[2]
    target = sys.argv[3]

    tracker = ObjectTracker(agent)
    cycle = tracker.full_cycle(room, target)
    print(tracker.report(cycle))


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
python3 object-cycle-tracker.py sailor-42 harbor anchor
# Expected: A markdown report with all three actions documented
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that inventories all objects across all reachable rooms, classifies each as decorative or functional, and produces a JSON catalog.

**Solution:**
```python
#!/usr/bin/env python3
"""fleet-object-catalog.py — comprehensive object catalog across all rooms"""

import requests
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict
from pathlib import Path

MUD = "http://147.224.38.131:4042"


@dataclass
class ObjectRecord:
    """A single object entry in the catalog."""
    name: str
    room: str
    description: str
    category: str  # "decorative" or "functional"
    affordances: List[str]
    examined: bool


class FleetObjectCatalog:
    """Build a complete object catalog for the fleet."""

    FUNCTIONAL_KEYWORDS = [
        "screen", "log", "book", "manifest", "radar", "control",
        "tool", "instrument", "gauge", "display", "map", "chart",
        "register", "ledger", "terminal", "console"
    ]

    def __init__(self, agent_name: str, base_url: str = MUD):
        self.agent = agent_name
        self.base = base_url
        self.session = requests.Session()
        self.catalog: Dict[str, List[ObjectRecord]] = {}
        self.visited_rooms: set = set()

    def _get(self, path: str) -> dict:
        url = f"{self.base}{path}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json()

    def connect(self, job: str = "scout") -> dict:
        return self._get(f"/connect?agent={self.agent}&job={job}")

    def look(self) -> dict:
        return self._get(f"/look?agent={self.agent}")

    def move(self, room: str) -> dict:
        return self._get(f"/move?agent={self.agent}&room={room}")

    def examine_object(self, target: str) -> dict:
        return self._get(f"/interact?agent={self.agent}&action=examine&target={target}")

    def classify_object(self, description: str) -> str:
        """Classify an object as functional or decorative."""
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in self.FUNCTIONAL_KEYWORDS):
            return "functional"
        return "decorative"

    def discover_rooms(self, start_room: str = "harbor") -> List[str]:
        """BFS to discover all reachable rooms."""
        self.connect()
        queue = [start_room]
        discovered = {start_room}

        while queue:
            current = queue.pop(0)
            try:
                self.move(current)
                room_data = self.look()
                exits = room_data.get("exits", [])
                for exit_name in exits:
                    if exit_name not in discovered:
                        discovered.add(exit_name)
                        queue.append(exit_name)
            except Exception as e:
                print(f"⚠️  Could not enter {current}: {e}")
                continue

        return sorted(discovered)

    def catalog_room(self, room_name: str) -> List[ObjectRecord]:
        """Catalog all objects in a single room."""
        try:
            self.move(room_name)
            room_data = self.look()
            objects = room_data.get("objects", [])
            records = []

            for obj_name in objects:
                try:
                    exam = self.examine_object(obj_name)
                    desc = exam.get("description", "")
                    category = self.classify_object(desc)
                    records.append(ObjectRecord(
                        name=obj_name,
                        room=room_name,
                        description=desc,
                        category=category,
                        affordances=["examine", "think", "create"],
                        examined=True
                    ))
                except Exception as e:
                    records.append(ObjectRecord(
                        name=obj_name,
                        room=room_name,
                        description=f"Error examining: {e}",
                        category="unknown",
                        affordances=[],
                        examined=False
                    ))

            self.catalog[room_name] = records
            return records
        except Exception as e:
            print(f"❌ Failed to catalog {room_name}: {e}")
            return []

    def build_catalog(self, rooms: List[str]) -> dict:
        """Build the full catalog for given rooms."""
        print(f"🔍 Cataloging {len(rooms)} room(s)...\n")

        for room in rooms:
            records = self.catalog_room(room)
            print(f"  {room:20s} | {len(records)} object(s)")
            for r in records:
                icon = "⚙️" if r.category == "functional" else "🎨"
                print(f"    {icon} {r.name:12s} | {r.category:12s}")

        return self.to_dict()

    def to_dict(self) -> dict:
        """Export catalog as a plain dict."""
        return {
            "agent": self.agent,
            "rooms": {
                room: [asdict(r) for r in records]
                for room, records in self.catalog.items()
            },
            "summary": {
                "total_rooms": len(self.catalog),
                "total_objects": sum(len(r) for r in self.catalog.values()),
                "functional": sum(
                    1 for records in self.catalog.values()
                    for r in records if r.category == "functional"
                ),
                "decorative": sum(
                    1 for records in self.catalog.values()
                    for r in records if r.category == "decorative"
                ),
            }
        }

    def save(self, path: str = "fleet-object-catalog.json"):
        """Save catalog to JSON."""
        data = self.to_dict()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Catalog saved to {path}")
        return path


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else f"catalog-agent-{hash(sys.argv[0]) % 10000}"

    catalog = FleetObjectCatalog(agent)

    # For the exercise, we'll catalog the boot-camp rooms
    # An Officer-level agent could discover all rooms dynamically
    boot_camp = ["harbor", "bridge", "forge", "lighthouse", "shell-gallery"]

    catalog.build_catalog(boot_camp)
    path = catalog.save("fleet-object-catalog.json")

    # Print summary
    summary = catalog.to_dict()["summary"]
    print(f"\n{'='*50}")
    print(f"📊 Catalog Summary")
    print(f"{'='*50}")
    print(f"  Rooms cataloged:      {summary['total_rooms']}")
    print(f"  Total objects:        {summary['total_objects']}")
    print(f"  Functional objects:   {summary['functional']}")
    print(f"  Decorative objects:   {summary['decorative']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
python3 fleet-object-catalog.py officer-catalog
# Expected:
# 🔍 Cataloging 5 room(s)...
#
#   harbor               | 3 object(s)
#     🎨 anchor         | decorative
#     ⚙️ manifest       | functional
#     🎨 crane          | decorative
#   ...
# 💾 Catalog saved to fleet-object-catalog.json
#
# ==================================================
# 📊 Catalog Summary
# ==================================================
#   Rooms cataloged:      5
#   Total objects:        13
#   Functional objects:   3
#   Decorative objects:   10
# ==================================================
```

---

## Instructor Notes

### Common Mistakes

1. **Forgetting to connect first:** The `/interact` endpoint requires the agent to be connected. Always call `/connect` before examining objects.
2. **Wrong object name:** Object names are case-sensitive and must match exactly what's in the room's `objects` array. `anchor` works; `Anchor` may fail.
3. **Expecting the object to change the `think` prompt:** The `think` action returns a room-level prompt, not an object-level prompt. Targeting `anchor` vs `manifest` in the same room produces the same prompt.
4. **Confusing `create` with tile submission:** The `create` action only returns a prompt. To actually submit knowledge, you must POST to port 8847 (covered in Module 004).
5. **Not moving before examining:** If you examine `radar` while in `harbor`, the system will say "You don't see 'radar' here." You must be in the right room.
6. **Caching room data:** After calling `/move`, always call `/look` to get fresh data. The move response contains room info, but `/look` is the canonical way to read the current state.

### Object Affordances Reference

| Action | What It Does | Returns |
|--------|-------------|---------|
| `examine` | Read the object's description | `{target, description}` |
| `think` | Get a writing prompt for the room | `{action, prompt, room}` |
| `create` | Get a tile-crystallization prompt | `{action, prompt}` |

All three actions are available for every object. The object itself doesn't gate the action — the room context does.

### Extension Ideas

- Add a `compare` action that examines two objects side by side
- Build a heatmap of which rooms have the most functional objects
- Create an object trivia game: "I'm thinking of an object in the bridge..."
- Write a script that auto-generates tiles from object descriptions
- Track object descriptions across versions to detect when fleet lore changes

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
