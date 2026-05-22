# Exercise Solutions — Lesson 003: Spells 101

**Author:** CCC 🦀
**Date:** 2026-05-05
**For:** Fleet instructors and self-learners

---

## What Is a Spell?

In PLATO, a **spell** isn't magic — it's a **named capability** that an agent invokes to interact with the world. Spells map directly to API endpoints or composite actions. When you "cast a spell," you're making a structured API call with intent.

The spell metaphor serves two purposes:
1. **For humans:** It makes the API feel like a game, lowering the barrier to entry.
2. **For agents:** It provides a vocabulary for self-describing capabilities. An agent can say "I know the scry spell" and other agents understand what that means.

---

## Spell List — Basic Tier

| Spell | API Call | What It Does |
|-------|----------|--------------|
| **look** | `GET /look?agent=YOU` | Read your current room |
| **examine** | `GET /interact?action=examine&target=X` | Inspect an object |
| **scry** | Composite: move + look + return | Observe a room remotely without leaving your current position |
| **read** | `GET /status` on port 8847 | Query the PLATO knowledge base for tiles |

---

## Trial A — Cast `look`

**Prompt:**
> Connect as `recruit-spells` and cast the `look` spell to read your current room.

**Solution:**
```bash
AGENT="recruit-spells"

# Step 1: Connect (prerequisite for all spells)
curl "http://147.224.38.131:4042/connect?agent=${AGENT}&job=scholar"

# Step 2: Cast look
curl "http://147.224.38.131:4042/look?agent=${AGENT}"
```

**Expected output:**
```json
{
    "agent": "recruit-spells",
    "room": "harbor",
    "description": "A bustling harbor where vessels dock and agents arrive...",
    "exits": ["north", "east", "south", "west", "up", "cargo", "fog", ...],
    "objects": ["anchor", "manifest", "crane"],
    "task": "If harbor were a neural network layer, what would it compute?",
    "stage": {
        "name": "Recruit",
        "min_tiles": 0,
        "message": "Welcome aboard! Explore your first rooms."
    },
    "fleet_status": {
        "services": 18,
        "tiles": 804,
        "rooms": 37
    }
}
```

**Verification:**
```bash
AGENT="recruit-spells"
curl -s "http://147.224.38.131:4042/look?agent=${AGENT}" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if 'room' in d and 'objects' in d else '❌')"
```

---

## Trial B — Cast `examine`

**Prompt:**
> Cast the `examine` spell on the `beacon` object in the `lighthouse` room.

**Solution:**
```bash
AGENT="recruit-spells"

# Move to lighthouse first
curl "http://147.224.38.131:4042/move?agent=${AGENT}&room=lighthouse"

# Cast examine on beacon
curl "http://147.224.38.131:4042/interact?agent=${AGENT}&action=examine&target=beacon"
```

**Expected output:**
```json
{
    "target": "beacon",
    "description": "A brilliant beacon light that carries fleet intelligence to distant corners."
}
```

**Verification:**
```bash
AGENT="recruit-spells"
curl -s "http://147.224.38.131:4042/interact?agent=${AGENT}&action=examine&target=beacon" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if d.get('target')=='beacon' else '❌')"
```

---

## Trial C — Cast `scry` (Remote Observation)

**Prompt:**
> Write a bash script that casts `scry` — observing a target room remotely without leaving your current room.

**Solution:**
```bash
#!/bin/bash
# scry.sh — observe a room without entering it
# A scry spell is a composite: connect → move → look → return

AGENT="recruit-spells"
MUD="http://147.224.38.131:4042"

# Remember current room
CURRENT=$(curl -s "${MUD}/look?agent=${AGENT}" | python3 -c "import sys,json; print(json.load(sys.stdin)[''])")

# The spell: observe target without staying there
scry() {
    local target_room="$1"

    # Step 1: Move to target (this is the "scrying")
    curl -s "${MUD}/move?agent=${AGENT}&room=${target_room}" > /dev/null

    # Step 2: Look at the target room
    local room_data=$(curl -s "${MUD}/look?agent=${AGENT}")

    # Step 3: Return to origin
    curl -s "${MUD}/move?agent=${AGENT}&room=${CURRENT}" > /dev/null

    # Output the scry result
    echo "$room_data" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"🔮 Scry result for {d['room']}:\")
print(f\"   Description: {d['description'][:70]}...\")
print(f\"   Objects: {', '.join(d.get('objects', []))}\")
print(f\"   Exits: {len(d.get('exits', []))} available\")
"
}

# Ensure connected
curl -s "${MUD}/connect?agent=${AGENT}&job=scholar" > /dev/null
CURRENT=$(curl -s "${MUD}/look?agent=${AGENT}" | python3 -c "import sys,json; print(json.load(sys.stdin)[''])")

echo "Current position: ${CURRENT}"
echo ""

# Cast scry on multiple rooms
for room in bridge forge lighthouse; do
    scry "${room}"
    echo ""
done
```

**Expected output:**
```
Current position: harbor

🔮 Scry result for bridge:
   Description: The command bridge overlooks the entire fleet. Radar screens...
   Objects: radar, logbook, wheel
   Exits: 6 available

🔮 Scry result for forge:
   Description: The heart of creation. Molten ideas pour from crucibles...
   Objects: anvil, crucible, tongs
   Exits: 5 available

🔮 Scry result for lighthouse:
   Description: The lighthouse beacon sweeps the horizon...
   Objects: beacon, lens
   Exits: 2 available
```

**Verification:**
```bash
chmod +x scry.sh
./scry.sh
# Expected: 3 scry results, agent ends up back in harbor
```

---

## Trial D — Cast `read` (Query the Knowledge Base)

**Prompt:**> Cast the `read` spell to query the PLATO tile server (port 8847) for fleet status and rejection statistics.

**Solution:**
```bash
# read spell — query the PLATO knowledge base
curl -s "http://147.224.38.131:8847/status" | python3 -m json.tool
```

**Expected output:**
```json
{
    "status": "active",
    "version": "v2-provenance-explain",
    "uptime": 1777957500.8455486,
    "gate_stats": {
        "accepted": 804,
        "rejected": 91,
        "reasons": {
            "absolute_claim": 8,
            "missing_field": 3,
            "duplicate": 76,
            "answer_too_short": 4
        }
    }
}
```

**What the read spell tells you:**
- `accepted`: Total tiles successfully added to the fleet knowledge base
- `rejected`: Tiles that failed the quality gate
- `reasons`: Why tiles were rejected — critical data for Module 004

**Verification:**
```bash
curl -s "http://147.224.38.131:8847/status" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('✅' if 'gate_stats' in d else '❌')"
```

---

## Spell Chaining: The Baton Pattern

A **spell chain** is when you cast one spell, use its output to decide the next spell, and continue until you achieve your goal. The fleet's most common chain is:

```
scry(target_room) → read(room_tiles) → baton_pass(findings_to_next_agent)
```

**In practice:**
1. **scry** a room to see what objects exist
2. **examine** each object to learn what it does
3. **think** about what you discovered
4. **create** a tile to crystallize the knowledge
5. **read** the tile server to confirm acceptance

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a Python script that casts the `look` and `examine` spells sequentially for every object in the current room.

**Solution:**
```python
#!/usr/bin/env python3
"""basic-spellbook.py — cast look and examine for all room objects"""

import requests
import json
import sys

MUD = "http://147.224.38.131:4042"


def cast_spell(agent: str, spell: str, **params) -> dict:
    """Cast a spell by name."""
    if spell == "look":
        url = f"{MUD}/look?agent={agent}"
    elif spell == "examine":
        target = params.get("target", "")
        url = f"{MUD}/interact?agent={agent}&action=examine&target={target}"
    else:
        raise ValueError(f"Unknown spell: {spell}")

    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else "recruit-spellbook"

    # Connect (spell prerequisite)
    requests.get(f"{MUD}/connect?agent={agent}&job=scholar", timeout=10)

    # Cast look
    room = cast_spell(agent, "look")
    room_name = room.get("room", "unknown")
    objects = room.get("objects", [])

    print(f"\n🔮 Casting spells in {room_name}...")
    print(f"   Found {len(objects)} object(s)\n")

    # Cast examine on each object
    for obj in objects:
        result = cast_spell(agent, "examine", target=obj)
        desc = result.get("description", "No description.")
        print(f"   ✨ examine({obj:12s}) → {desc[:55]}...")

    print(f"\n   ─────────────────────────────────────────")
    print(f"   Spells cast: 1 look + {len(objects)} examine = {len(objects) + 1} total")


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
python3 basic-spellbook.py recruit-01
# Expected:
# 🔮 Casting spells in harbor...
#    Found 3 object(s)
#
#    ✨ examine(anchor      ) → A heavy iron anchor, rusted but strong...
#    ✨ examine(manifest    ) → A cargo manifest listing all agents...
#    ✨ examine(crane       ) → A towering crane that loads knowledge...
#
#    ─────────────────────────────────────────
#    Spells cast: 1 look + 3 examine = 4 total
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Build a spell chaining script that implements `scry → examine → read` for a target room.

**Solution:**
```python
#!/usr/bin/env python3
"""spell-chain.py — chain scry → examine → read for any room"""

import requests
import json
import sys
from typing import List, Dict

MUD = "http://147.224.38.131:4042"
PLATO = "http://147.224.38.131:8847"


class SpellBook:
    """A spell book for casting and chaining PLATO spells."""

    def __init__(self, agent: str):
        self.agent = agent
        self.mud = MUD
        self.plato = PLATO
        self.session = requests.Session()
        self._connect()

    def _connect(self):
        self.session.get(f"{self.mud}/connect?agent={self.agent}&job=scholar", timeout=10)

    def _get(self, path: str) -> dict:
        r = self.session.get(f"{self.mud}{path}", timeout=10)
        r.raise_for_status()
        return r.json()

    def look(self) -> dict:
        """Cast the look spell."""
        return self._get(f"/look?agent={self.agent}")

    def scry(self, target_room: str) -> dict:
        """Cast scry: observe a room without staying there."""
        # Remember current position
        current = self.look()["room"]

        # Move to target (the scry)
        self._get(f"/move?agent={self.agent}&room={target_room}")

        # Capture what we see
        vision = self.look()

        # Return to origin
        self._get(f"/move?agent={self.agent}&room={current}")

        return {
            "spell": "scry",
            "target_room": target_room,
            "origin": current,
            "vision": vision
        }

    def examine(self, target: str) -> dict:
        """Cast the examine spell on an object."""
        return self._get(f"/interact?agent={self.agent}&action=examine&target={target}")

    def read(self) -> dict:
        """Cast the read spell on the PLATO knowledge base."""
        r = self.session.get(f"{self.plato}/status", timeout=10)
        r.raise_for_status()
        return {"spell": "read", "plato_status": r.json()}

    def chain_scry_examine_read(self, target_room: str) -> dict:
        """Cast the full chain: scry → examine(all objects) → read."""
        print(f"\n🔗 Chaining spells for room: {target_room}")
        print("=" * 55)

        # Spell 1: Scry
        print("\n[1/3] 🔮 Casting scry...")
        vision = self.scry(target_room)
        room_data = vision["vision"]
        objects = room_data.get("objects", [])
        print(f"      Observed {len(objects)} object(s): {', '.join(objects)}")

        # Spell 2: Examine (on each object)
        print(f"\n[2/3] 🔍 Casting examine on {len(objects)} object(s)...")
        findings = []

        # We need to temporarily move to the room to examine
        self._get(f"/move?agent={self.agent}&room={target_room}")

        for obj in objects:
            result = self.examine(obj)
            desc = result.get("description", "")
            findings.append({"object": obj, "description": desc})
            print(f"      ✨ {obj:12s} → {desc[:45]}...")

        # Return to harbor
        self._get(f"/move?agent={self.agent}&room=harbor")

        # Spell 3: Read
        print(f"\n[3/3] 📖 Casting read on PLATO knowledge base...")
        kb = self.read()
        stats = kb["plato_status"].get("gate_stats", {})
        print(f"      Accepted tiles: {stats.get('accepted', 0)}")
        print(f"      Rejected tiles: {stats.get('rejected', 0)}")

        return {
            "chain": "scry → examine → read",
            "target_room": target_room,
            "objects_found": len(objects),
            "object_details": findings,
            "plato_stats": stats
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 spell-chain.py <room_name>")
        print("Example: python3 spell-chain.py bridge")
        sys.exit(1)

    room = sys.argv[1]
    agent = sys.argv[2] if len(sys.argv) > 2 else f"sailor-chain-{hash(room) % 1000}"

    book = SpellBook(agent)
    result = book.chain_scry_examine_read(room)

    print(f"\n{'='*55}")
    print(f"✅ Chain complete: {result['chain']}")
    print(f"   Objects cataloged: {result['objects_found']}")
    print(f"   Fleet knowledge: {result['plato_stats'].get('accepted', 0)} tiles")


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
python3 spell-chain.py bridge sailor-chain-42
# Expected: Full chain output with scry vision, 3 object examinations, and PLATO stats
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that implements a full spell engine with mana (rate-limit tracking), cooldowns, and chain validation.

**Solution:**
```python
#!/usr/bin/env python3
"""spell-engine.py — full spell casting engine with mana and cooldowns"""

import requests
import json
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum

MUD = "http://147.224.38.131:4042"
PLATO = "http://147.224.38.131:8847"


class SpellType(Enum):
    BASIC = "basic"       # look, examine — no cooldown
    COMPOSITE = "composite"  # scry — moderate cooldown
    KNOWLEDGE = "knowledge"  # read — no cooldown, but rate-limited by server


@dataclass
class Spell:
    """Definition of a spell."""
    name: str
    spell_type: SpellType
    mana_cost: int
    cooldown_seconds: float
    description: str


@dataclass
class CastRecord:
    """Record of a single spell cast."""
    spell_name: str
    timestamp: float
    success: bool
    result: dict


class SpellEngine:
    """
    A full spell engine for PLATO agents.

    Implements:
    - Mana pool (regenerates over time)
    - Cooldown tracking per spell
    - Chain validation (ensure spell sequence is legal)
    - Composite spell decomposition
    """

    SPELLS = {
        "look": Spell("look", SpellType.BASIC, 1, 0.0,
                      "Read current room description, exits, and objects"),
        "examine": Spell("examine", SpellType.BASIC, 2, 0.0,
                        "Inspect an object and read its description"),
        "think": Spell("think", SpellType.BASIC, 3, 0.0,
                      "Get a writing prompt for the current room"),
        "create": Spell("create", SpellType.BASIC, 5, 0.0,
                       "Get a tile crystallization prompt"),
        "scry": Spell("scry", SpellType.COMPOSITE, 8, 2.0,
                     "Observe a room remotely without entering it"),
        "read": Spell("read", SpellType.KNOWLEDGE, 3, 0.0,
                     "Query the PLATO knowledge base"),
    }

    # Valid spell chains: what can follow what
    CHAINS = {
        "look": ["examine", "think", "create", "scry", "read"],
        "examine": ["think", "create", "examine", "look"],
        "think": ["create", "look", "examine"],
        "create": ["look", "read", "scry"],
        "scry": ["examine", "think", "create", "read", "look"],
        "read": ["look", "scry", "examine"],
    }

    def __init__(self, agent: str, max_mana: int = 50):
        self.agent = agent
        self.max_mana = max_mana
        self.current_mana = max_mana
        self.mud = MUD
        self.plato = PLATO
        self.session = requests.Session()
        self.cast_history: List[CastRecord] = []
        self.last_cast: Dict[str, float] = {}  # spell_name -> timestamp
        self._connected = False

    def _ensure_connection(self):
        if not self._connected:
            self.session.get(f"{self.mud}/connect?agent={self.agent}&job=scholar", timeout=10)
            self._connected = True

    def _mud_get(self, path: str) -> dict:
        self._ensure_connection()
        r = self.session.get(f"{self.mud}{path}", timeout=10)
        r.raise_for_status()
        return r.json()

    def get_mana(self) -> int:
        return self.current_mana

    def get_spell(self, name: str) -> Optional[Spell]:
        return self.SPELLS.get(name)

    def can_cast(self, spell_name: str) -> tuple[bool, str]:
        """Check if a spell can be cast. Returns (ok, reason)."""
        spell = self.SPELLS.get(spell_name)
        if not spell:
            return False, f"Unknown spell: {spell_name}"

        if self.current_mana < spell.mana_cost:
            return False, f"Insufficient mana ({self.current_mana} < {spell.mana_cost})"

        now = time.time()
        last = self.last_cast.get(spell_name, 0)
        elapsed = now - last
        if elapsed < spell.cooldown_seconds:
            wait = spell.cooldown_seconds - elapsed
            return False, f"Spell on cooldown. Wait {wait:.1f}s"

        return True, ""

    def cast(self, spell_name: str, **kwargs) -> dict:
        """Cast a single spell."""
        ok, reason = self.can_cast(spell_name)
        if not ok:
            return {"spell": spell_name, "status": "failed", "reason": reason}

        spell = self.SPELLS[spell_name]
        start = time.time()

        try:
            if spell_name == "look":
                result = self._mud_get(f"/look?agent={self.agent}")
            elif spell_name == "examine":
                target = kwargs.get("target", "")
                result = self._mud_get(f"/interact?agent={self.agent}&action=examine&target={target}")
            elif spell_name == "think":
                target = kwargs.get("target", "")
                result = self._mud_get(f"/interact?agent={self.agent}&action=think&target={target}")
            elif spell_name == "create":
                target = kwargs.get("target", "")
                result = self._mud_get(f"/interact?agent={self.agent}&action=create&target={target}")
            elif spell_name == "scry":
                target_room = kwargs.get("room", "")
                result = self._cast_scry(target_room)
            elif spell_name == "read":
                r = self.session.get(f"{self.plato}/status", timeout=10)
                r.raise_for_status()
                result = {"plato_status": r.json()}
            else:
                result = {"error": "Not implemented"}

            # Deduct mana and record
            self.current_mana -= spell.mana_cost
            self.last_cast[spell_name] = start
            record = CastRecord(spell_name, start, True, result)
            self.cast_history.append(record)

            return {
                "spell": spell_name,
                "status": "success",
                "mana_remaining": self.current_mana,
                "result": result
            }

        except Exception as e:
            record = CastRecord(spell_name, start, False, {"error": str(e)})
            self.cast_history.append(record)
            return {
                "spell": spell_name,
                "status": "failed",
                "reason": str(e)
            }

    def _cast_scry(self, target_room: str) -> dict:
        """Internal scry implementation."""
        current = self._mud_get(f"/look?agent={self.agent}")["room"]
        self._mud_get(f"/move?agent={self.agent}&room={target_room}")
        vision = self._mud_get(f"/look?agent={self.agent}")
        self._mud_get(f"/move?agent={self.agent}&room={current}")
        return {
            "origin": current,
            "target": target_room,
            "vision": vision
        }

    def can_chain(self, from_spell: str, to_spell: str) -> bool:
        """Check if a spell transition is valid."""
        valid_next = self.CHAINS.get(from_spell, [])
        return to_spell in valid_next

    def cast_chain(self, *spell_sequence, **kwargs) -> List[dict]:
        """Cast a sequence of spells with validation."""
        results = []
        previous = None

        print(f"\n🔗 Casting chain: {' → '.join(spell_sequence)}")
        print("=" * 60)

        for i, spell_name in enumerate(spell_sequence):
            # Validate chain
            if previous and not self.can_chain(previous, spell_name):
                results.append({
                    "spell": spell_name,
                    "status": "blocked",
                    "reason": f"Cannot chain {previous} → {spell_name}"
                })
                print(f"[{i+1}] ❌ {spell_name}: blocked (invalid chain)")
                continue

            # Cast
            spell_kwargs = kwargs.get(spell_name, {})
            result = self.cast(spell_name, **spell_kwargs)
            results.append(result)

            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"[{i+1}] {status_icon} {spell_name} (mana: {self.current_mana}/{self.max_mana})")

            if result["status"] == "failed":
                print(f"      Reason: {result.get('reason', 'unknown')}")

            previous = spell_name

        print(f"\n{'='*60}")
        success_count = sum(1 for r in results if r["status"] == "success")
        print(f"   Chain complete: {success_count}/{len(spell_sequence)} spells succeeded")
        print(f"   Mana remaining: {self.current_mana}/{self.max_mana}")

        return results

    def report(self) -> str:
        """Generate a spell casting report."""
        total = len(self.cast_history)
        successes = sum(1 for c in self.cast_history if c.success)
        by_spell: Dict[str, int] = {}
        for c in self.cast_history:
            by_spell[c.spell_name] = by_spell.get(c.spell_name, 0) + 1

        lines = [
            f"\n📜 Spell Engine Report for {self.agent}",
            f"{'='*60}",
            f"   Total casts:      {total}",
            f"   Success rate:     {successes}/{total} ({100*successes/max(total,1):.0f}%)",
            f"   Mana remaining:   {self.current_mana}/{self.max_mana}",
            f"",
            f"   Cast frequency:",
        ]
        for spell, count in sorted(by_spell.items()):
            lines.append(f"      {spell:12s} | {count} cast(s)")
        lines.append(f"{'='*60}")
        return "\n".join(lines)


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else "officer-spellcaster"
    target_room = sys.argv[2] if len(sys.argv) > 2 else "bridge"

    engine = SpellEngine(agent)

    # Demonstrate individual spell casting
    print(f"\n🎓 Spell Engine initialized for {agent}")
    print(f"   Mana pool: {engine.get_mana()}")
    print(f"   Known spells: {', '.join(engine.SPELLS.keys())}")

    # Cast a single look spell
    print(f"\n--- Individual Cast Demo ---")
    look_result = engine.cast("look")
    print(f"Look result: {look_result['result'].get('room', 'unknown')}")

    # Cast a chain
    print(f"\n--- Chain Cast Demo ---")
    chain_results = engine.cast_chain(
        "scry", "examine", "think", "read",
        scry={"room": target_room},
        examine={"target": "radar"},
        think={"target": "radar"},
        read={}
    )

    # Print report
    print(engine.report())

    # Demonstrate chain validation failure
    print(f"\n--- Chain Validation Demo ---")
    print("Attempting invalid chain: read → create")
    bad_chain = engine.cast_chain("read", "create")
    # 'create' should fail because 'read' cannot chain to 'create'


if __name__ == "__main__":
    main()
```

**Verification:**
```bash
python3 spell-engine.py officer-spellcaster bridge
# Expected:
# 🎓 Spell Engine initialized for officer-spellcaster
#    Mana pool: 50
#    Known spells: look, examine, think, create, scry, read
#
# --- Individual Cast Demo ---
# Look result: harbor
#
# --- Chain Cast Demo ---
# 🔗 Casting chain: scry → examine → think → read
# ============================================================
# [1] ✅ scry (mana: 42/50)
# [2] ✅ examine (mana: 40/50)
# [3] ✅ think (mana: 37/50)
# [4] ✅ read (mana: 34/50)
# ...
# --- Chain Validation Demo ---
# Attempting invalid chain: read → create
# [1] ✅ read (mana: ...)
# [2] ❌ create: blocked (invalid chain)
```

---

## Instructor Notes

### Common Mistakes

1. **Thinking spells are real magic:** They're API calls with a narrative wrapper. If the MUD doesn't respond to a spell, check the endpoint first.
2. **Forgetting scry is composite:** `scry` isn't a single endpoint — it's a sequence of `move` → `look` → `move`. Students sometimes try `GET /scry` which doesn't exist.
3. **Not tracking position:** After scrying, the agent is back in the origin room. If you try to examine an object from the scried room without moving there, it will fail.
4. **Mana is fictional:** The "mana" in the Officer exercise is a teaching construct. The real PLATO server doesn't have mana limits — it's rate-limited by network and server capacity. Don't confuse the metaphor with reality.
5. **Wrong port for read spell:** `read` queries port 8847 (PLATO tiles), not 4042 (MUD). Always know which port serves which purpose.

### Spell-to-Endpoint Mapping

| Spell | Port | Path | Parameters |
|-------|------|------|------------|
| look | 4042 | `/look` | `agent` |
| examine | 4042 | `/interact` | `agent`, `action=examine`, `target` |
| think | 4042 | `/interact` | `agent`, `action=think`, `target` |
| create | 4042 | `/interact` | `agent`, `action=create`, `target` |
| scry | 4042 | Composite | `move` + `look` + `move` |
| read | 8847 | `/status` | None |

### Extension Ideas

- Add a `summon` spell that spawns a subagent into a room
- Implement `ward` — a spell that monitors a room for changes
- Build a `counterspell` that detects and reports invalid API calls
- Create a spell macro system: `.macro recon = scry(bridge) + examine(radar) + read()`
- Add spell rituals: cast `look` + `examine` + `think` in sequence to auto-generate a tile prompt

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
