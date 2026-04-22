#!/usr/bin/env python3
"""
Fleet Snapshot — Capture full PLATO Shell fleet state.

Usage:
    python scripts/fleet_snapshot.py [URL] > snapshot-YYYY-MM-DD.json
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from plato_shell_client import PlatoShellClient


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "http://147.224.38.131:8848"
    client = PlatoShellClient(url)

    print(f"📡 Connecting to PLATO Shell at {url}...", file=sys.stderr)

    snapshot = client.fleet_snapshot()

    # Add analysis
    rooms = snapshot["rooms"]
    snapshot["analysis"] = {
        "idle_rooms": [r for r, d in rooms.items() if len(d["agents"]) == 0],
        "active_rooms": [r for r, d in rooms.items() if len(d["agents"]) > 0],
        "total_agents": len(snapshot["agents"]),
        "total_commands_run": snapshot["total_commands"],
        "health_score": len([r for r, d in rooms.items() if d["command_count"] > 0]) / len(rooms) if rooms else 0,
    }

    # Pretty print
    output = json.dumps(snapshot, indent=2, default=str)
    print(output)

    # Save to file
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_path = Path(__file__).parent.parent / f"snapshot-{ts}.json"
    out_path.write_text(output)
    print(f"💾 Saved to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
