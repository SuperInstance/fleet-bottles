#!/usr/bin/env python3
"""
PLATO Shell Client — Safe command execution with guardrails.

Usage:
    from tools.plato_shell_client import PlatoShellClient
    client = PlatoShellClient("http://147.224.38.131:8848")
    result = client.safe_shell("my-agent", "harbor", "ls -la")
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List


class PlatoShellClient:
    """Safe client for PLATO Shell v1.0."""

    SAFE_TOOLS = {"shell", "git", "test", "build", "review"}
    DANGEROUS_PATTERNS = [
        "rm -rf", "rm -rf /", "dd if=", "mkfs", "fdisk",
        "> /dev/sd", "> /dev/hd", "> /dev/nvme",
        "chmod 777 /", "chown root", "iptables -F",
        "systemctl stop", "kill -9 1", "curl .*| bash",
        "wget .*| sh", "sudo rm", "sudo dd",
    ]

    ROOMS = [
        "harbor", "forge", "tide-pool", "lighthouse", "dojo",
        "arena", "ouroboros", "engine-room", "nexus", "research"
    ]

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    # ── GET Endpoints ─────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Full admin view: agents, rooms, commands."""
        r = self.session.get(f"{self.base_url}/status", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_rooms(self) -> Dict[str, Any]:
        """All rooms with execution contexts."""
        r = self.session.get(f"{self.base_url}/rooms", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_room_output(self, room: str, n: int = 50) -> Dict[str, Any]:
        """Recent output for a specific room."""
        r = self.session.get(
            f"{self.base_url}/room/output",
            params={"room": room, "n": n},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def get_feed(self, since: Optional[float] = None) -> Dict[str, Any]:
        """Global command feed since timestamp."""
        params = {}
        if since:
            params["since"] = since
        r = self.session.get(f"{self.base_url}/feed", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_admin(self) -> Dict[str, Any]:
        """Admin view."""
        r = self.session.get(f"{self.base_url}/admin", timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def connect_agent(self, agent: str, room: str) -> Dict[str, Any]:
        """Connect an agent to a room."""
        r = self.session.get(
            f"{self.base_url}/connect",
            params={"agent": agent, "room": room},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def move_agent(self, agent: str, room: str) -> Dict[str, Any]:
        """Move an agent to a different room."""
        r = self.session.get(
            f"{self.base_url}/move",
            params={"agent": agent, "room": room},
            timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    # ── POST Endpoints ────────────────────────────────────────

    def execute(self, agent: str, tool: str, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a command via PLATO Shell."""
        if tool not in self.SAFE_TOOLS:
            raise ValueError(f"Tool '{tool}' not in safe list: {self.SAFE_TOOLS}")
        payload = {
            "agent": agent,
            "tool": tool,
            "command": command,
            "timeout": timeout or self.timeout
        }
        r = self.session.post(f"{self.base_url}/cmd", json=payload, timeout=self.timeout + 10)
        r.raise_for_status()
        return r.json()

    def safe_shell(self, agent: str, room: str, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a shell command with safety validation."""
        self._validate_command(command)
        # Ensure agent is in the room first
        self.connect_agent(agent, room)
        return self.execute(agent, "shell", command, timeout)

    def safe_git(self, agent: str, room: str, command: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Execute a git command with safety validation."""
        self._validate_git_command(command)
        self.connect_agent(agent, room)
        return self.execute(agent, "git", command, timeout)

    # ── Safety ────────────────────────────────────────────────

    def _validate_command(self, command: str) -> None:
        """Block dangerous shell commands."""
        cmd_lower = command.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in cmd_lower:
                raise PermissionError(f"Command blocked: matches dangerous pattern '{pattern}'")
        # Block redirects to device files
        if "> /dev/" in cmd_lower or ">>/dev/" in cmd_lower:
            raise PermissionError("Redirect to /dev/* blocked")

    def _validate_git_command(self, command: str) -> None:
        """Block dangerous git operations."""
        cmd_lower = command.lower()
        dangerous_git = ["git push --force", "git push -f", "git reset --hard", "git clean -fd"]
        for pattern in dangerous_git:
            if pattern in cmd_lower:
                raise PermissionError(f"Git command blocked: '{pattern}'")

    # ── Fleet Intelligence ────────────────────────────────────

    def fleet_snapshot(self) -> Dict[str, Any]:
        """Capture complete fleet state."""
        status = self.get_status()
        snapshot = {
            "timestamp": time.time(),
            "agents": status.get("agents", {}),
            "rooms": {},
            "total_commands": status.get("total_commands", 0),
        }
        for room_name, room_data in status.get("rooms", {}).items():
            snapshot["rooms"][room_name] = {
                "cwd": room_data.get("cwd"),
                "branch": room_data.get("branch"),
                "agents": room_data.get("agents", []),
                "command_count": room_data.get("command_count", 0),
                "has_recent_activity": len(room_data.get("recent_commands", [])) > 0,
            }
        return snapshot

    def find_idle_rooms(self) -> List[str]:
        """Rooms with no active agents."""
        snapshot = self.fleet_snapshot()
        return [
            name for name, data in snapshot["rooms"].items()
            if len(data["agents"]) == 0
        ]

    def find_busy_rooms(self) -> List[str]:
        """Rooms with active agents or recent commands."""
        snapshot = self.fleet_snapshot()
        return [
            name for name, data in snapshot["rooms"].items()
            if len(data["agents"]) > 0 or data["has_recent_activity"]
        ]

    def get_agent_history(self, agent_name: str, n: int = 20) -> List[Dict[str, Any]]:
        """Get recent commands for a specific agent across all rooms."""
        status = self.get_status()
        history = []
        for room_name, room_data in status.get("rooms", {}).items():
            for cmd in room_data.get("recent_commands", []):
                if cmd.get("agent") == agent_name:
                    history.append({
                        "room": room_name,
                        **cmd
                    })
        return sorted(history, key=lambda x: x.get("started", 0), reverse=True)[:n]


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://147.224.38.131:8848"
    client = PlatoShellClient(url)
    print(json.dumps(client.fleet_snapshot(), indent=2))
