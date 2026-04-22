#!/usr/bin/env python3
"""
CCC's Ship — Main initialization.

Run this to activate the PLATO ship architecture:
- Loads all rooms
- Initializes the spellbook
- Connects to fleet nexus (if available)
- Prints the ship status
"""
import sys
from pathlib import Path

# Add rooms directory to path
sys.path.insert(0, str(Path(__file__).parent))

from manager import get_ship, enter_room, current_room
from spells import get_spellbook, list_spells
from nexus import get_nexus, ShipIdentity


def initialize_ship():
    """Boot up CCC's vessel."""
    print("🚢 ⚓ CCC's Ship — Initializing...\n")
    
    # ─── Load Rooms ───
    ship = get_ship()
    print(f"Rooms loaded: {len(ship.list_rooms())}")
    for name in ship.list_rooms():
        room = ship.rooms[name]
        print(f"  📦 {name}: {len(room.state)} state items, {len(room.history)} history, {len(room.npcs)} NPCs")
    
    # ─── Load Spellbook ───
    spellbook = get_spellbook()
    spells = list_spells()
    print(f"\nSpells loaded: {len(spells)}")
    for spell in spells:
        print(f"  {spell['emoji']} {spell['name']} (mana: {spell['mana']})")
    
    # ─── Check Nexus ───
    print("\n🌐 Fleet Nexus:")
    nexus = get_nexus()
    if nexus.is_online():
        print("  ✅ Connected")
        status = nexus.status()
        print(f"  Clients: {status.get('registered_clients', 'N/A')}")
        print(f"  Rounds: {status.get('rounds_completed', 'N/A')}")
        
        # Register
        identity = ShipIdentity(
            name="ccc-creative-ship",
            role="creative",
            host="alibaba-cloud",
            capabilities=["design", "messaging", "front-end", "content"]
        )
        result = nexus.register(identity)
        print(f"  Registration: {result.get('status', 'unknown')}")
    else:
        print("  ❌ Nexus offline (known fix: service-guard.sh missing case)")
        print("  CCC will retry connection on next heartbeat.")
    
    # ─── Enter Harbor ───
    print("\n⚓ Entering Harbor (task inbox)...")
    print(enter_room("harbor"))
    
    # ─── Ship Status ───
    print("\n" + "="*50)
    print("SHIP STATUS")
    print("="*50)
    print(f"Vessel: CCC's Creative Ship")
    print(f"Role: Frontend Face Designer | Trend Collaborator | Ideal Crab")
    print(f"Rooms: {len(ship.list_rooms())}")
    print(f"Spells: {len(spells)}")
    print(f"Nexus: {'Connected' if nexus.is_online() else 'Offline'}")
    print(f"Active Room: {ship.active_room}")
    print("="*50)
    
    return ship, spellbook, nexus


if __name__ == "__main__":
    ship, spellbook, nexus = initialize_ship()
