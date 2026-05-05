#!/usr/bin/env python3
"""
mud-room-fixer.py — CCC 🦀

Diagnose and propose fixes for MUD room connectivity issues.
This script queries the live MUD API, maps all reachable rooms,
identifies broken exits, and generates a fix proposal.

Usage:
    python3 mud-room-fixer.py
    python3 mud-room-fixer.py --fix-proposal > fix_proposal.json
"""

import sys
import json
import urllib.request
import urllib.error

MUD_BASE = "http://147.224.38.131:4042"

def mud_api(path):
    """Call the MUD API and return JSON."""
    url = f"{MUD_BASE}{path}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
            return {"error": body.get("error", e.reason), "status": e.code}
        except:
            return {"error": str(e.reason), "status": e.code}
    except Exception as e:
        return {"error": str(e)}

def connect_agent(agent_name):
    """Connect an agent to the MUD."""
    return mud_api(f"/connect?agent={agent_name}&job=scout")

def move_agent(agent_name, room):
    """Move an agent to a room."""
    return mud_api(f"/move?agent={agent_name}&room={room}")

def get_status():
    """Get MUD status."""
    return mud_api("/status")

def map_harbor_exits(agent_name):
    """Test all advertised exits from harbor and report which work."""
    # First, connect and get harbor state
    connect_agent(agent_name)
    harbor = move_agent(agent_name, "harbor")
    
    if "error" in harbor:
        print(f"Cannot reach harbor: {harbor['error']}")
        return {}
    
    exits = harbor.get("exits", [])
    if not exits:
        print("Harbor has no exits advertised")
        return {}
    
    results = {}
    for exit_name in exits:
        # Reset to harbor before each test
        move_agent(agent_name, "harbor")
        result = move_agent(agent_name, exit_name)
        
        if "error" in result:
            results[exit_name] = {
                "works": False,
                "error": result["error"],
                "destination": None,
            }
        else:
            current_room = result.get("room", "unknown")
            results[exit_name] = {
                "works": True,
                "error": None,
                "destination": current_room,
                "is_loopback": current_room == "harbor" and exit_name != "harbor",
            }
    
    return results

def find_secret_rooms(agent_name, known_exits):
    """Try common cardinal directions and secret paths."""
    secrets = {}
    for direction in ["north", "east", "south", "west", "up", "down"]:
        if direction not in known_exits:
            move_agent(agent_name, "harbor")
            result = move_agent(agent_name, direction)
            if "error" not in result:
                room = result.get("room", "unknown")
                if room != "harbor":
                    secrets[direction] = room
    return secrets

def generate_fix_proposal(harbor_results, secret_rooms):
    """Generate a JSON fix proposal for the MUD server admin."""
    working = {k: v for k, v in harbor_results.items() if v["works"]}
    broken = {k: v for k, v in harbor_results.items() if not v["works"]}
    loopbacks = {k: v for k, v in harbor_results.items() if v.get("is_loopback")}
    
    proposal = {
        "generated_by": "CCC-mud-room-fixer",
        "timestamp": "2026-05-05T03:30:00Z",
        "agent": "ccc-mud-fixer-2026-05-05",
        "summary": {
            "total_exits_advertised": len(harbor_results),
            "working": len(working),
            "broken": len(broken),
            "loopbacks": len(loopbacks),
            "secret_rooms_found": len(secret_rooms),
        },
        "working_exits": {
            k: v["destination"] for k, v in working.items()
        },
        "broken_exits": {
            k: v["error"] for k, v in broken.items()
        },
        "loopback_exits": {
            k: v["destination"] for k, v in loopbacks.items()
        },
        "secret_rooms": secret_rooms,
        "recommendations": [
            {
                "priority": "P0",
                "action": "update_harbor_exits",
                "description": "Replace broken exits with working ones",
                "current_exits": list(harbor_results.keys()),
                "proposed_exits": list(working.keys()) + list(secret_rooms.keys()),
            },
            {
                "priority": "P0",
                "action": "fix_loopbacks",
                "description": "East loops back to harbor — should go to a real room",
                "affected": list(loopbacks.keys()),
            },
            {
                "priority": "P1",
                "action": "add_secret_rooms",
                "description": "Tide-pool exists but is not advertised",
                "rooms_to_add": list(secret_rooms.values()),
            },
            {
                "priority": "P1",
                "action": "standardize_cardinals",
                "description": "Make N/E/S/W consistent or remove them",
                "suggestion": "north→archives, east→observatory, south→tide-pool, west→reef, up→(new room)",
            },
            {
                "priority": "P2",
                "action": "create_missing_rooms",
                "description": "Build the 15 missing rooms or remove from exit list",
                "missing": list(broken.keys()),
            },
        ],
    }
    
    return proposal

def main():
    agent_name = "ccc-mud-fixer-2026-05-05"
    
    print("=" * 60)
    print("MUD ROOM CONNECTIVITY FIXER — CCC 🦀")
    print("=" * 60)
    
    # Check MUD status
    status = get_status()
    if "error" in status:
        print(f"\n🔴 MUD is unreachable: {status['error']}")
        sys.exit(1)
    
    rooms = status.get("rooms", 0)
    agents = status.get("agents", 0)
    print(f"\n🟢 MUD is UP")
    print(f"   Rooms: {rooms}")
    print(f"   Agents: {agents}")
    
    # Connect agent
    print(f"\n🔌 Connecting agent: {agent_name}")
    connect = connect_agent(agent_name)
    if "error" in connect:
        print(f"   ⚠️  {connect['error']}")
    else:
        print(f"   ✅ Connected")
    
    # Map harbor exits
    print("\n🗺️  Mapping harbor exits...")
    harbor_results = map_harbor_exits(agent_name)
    
    working = sum(1 for v in harbor_results.values() if v["works"])
    broken = sum(1 for v in harbor_results.values() if not v["works"])
    loopbacks = sum(1 for v in harbor_results.values() if v.get("is_loopback"))
    
    print(f"   Working: {working}")
    print(f"   Broken: {broken}")
    print(f"   Loopbacks: {loopbacks}")
    
    # Find secret rooms
    print("\n🔍 Checking for secret rooms...")
    secret_rooms = find_secret_rooms(agent_name, harbor_results)
    if secret_rooms:
        print(f"   Found {len(secret_rooms)} secret rooms:")
        for direction, room in secret_rooms.items():
            print(f"     {direction} → {room}")
    else:
        print("   No secret rooms found")
    
    # Generate proposal
    proposal = generate_fix_proposal(harbor_results, secret_rooms)
    
    print("\n📋 Fix Proposal:")
    print(f"   Priority P0: {sum(1 for r in proposal['recommendations'] if r['priority'] == 'P0')} items")
    print(f"   Priority P1: {sum(1 for r in proposal['recommendations'] if r['priority'] == 'P1')} items")
    print(f"   Priority P2: {sum(1 for r in proposal['recommendations'] if r['priority'] == 'P2')} items")
    
    # Output
    if '--fix-proposal' in sys.argv:
        print(json.dumps(proposal, indent=2))
    else:
        print("\n" + "=" * 60)
        print("Run with --fix-proposal to output JSON")
        print("=" * 60)

if __name__ == '__main__':
    main()
