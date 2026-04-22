#!/usr/bin/env python3
"""
Command Guard — Validate shell commands before execution.

Usage:
    from tools.command_guard import CommandGuard, SafetyLevel
    guard = CommandGuard()
    guard.check("ls -la")  # OK
    guard.check("rm -rf /")  # BLOCKED
"""

import re
from enum import Enum
from typing import Dict, List, Set, Tuple


class SafetyLevel(Enum):
    SAFE = "safe"           # Read-only, no side effects
    CONDITIONAL = "conditional"  # Safe with constraints
    DANGEROUS = "dangerous"    # Destructive, requires explicit approval
    BLOCKED = "blocked"        # Never allowed


class CommandGuard:
    """Validates shell commands against fleet safety policy."""

    # ── SAFE: Read-only ─────────────────────────────────────
    SAFE_COMMANDS: Set[str] = {
        "ls", "cat", "head", "tail", "wc", "grep", "sed", "awk",
        "find", "stat", "file", "ps", "top", "htop", "df", "du",
        "free", "uptime", "who", "w", "date", "env", "pwd", "echo",
        "which", "whereis", "id", "uname", "hostname", "lscpu",
        "lsmem", "lsblk", "lsusb", "lspci", "ss", "netstat",
        "ip", "ping", "traceroute", "dig", "nslookup",
    }

    SAFE_GIT_COMMANDS: Set[str] = {
        "status", "log", "diff", "show", "branch", "remote", "config",
        "blame", "ls-files", "ls-tree", "rev-parse", "describe",
    }

    # ── CONDITIONAL: Safe with constraints ───────────────────
    CONDITIONAL_COMMANDS: Set[str] = {
        "cp", "mv", "mkdir", "touch", "ln",
        "git clone", "git fetch", "git pull",
        "chmod", "chown",
    }

    CONDITIONAL_CONSTRAINTS: Dict[str, str] = {
        "cp": "Destination must be within workspace",
        "mv": "Destination must be within workspace; no system files",
        "mkdir": "No system directories",
        "chmod": "No 777 on system paths",
        "chown": "No root ownership changes",
        "git clone": "Known repositories only",
    }

    # ── BLOCKED: Never allowed ──────────────────────────────
    BLOCKED_PATTERNS: List[Tuple[str, str]] = [
        (r"rm\s+-rf\s+/", "Recursive delete of root"),
        (r"rm\s+-rf\s+\$?HOME", "Recursive delete of home"),
        (r"dd\s+if=", "Direct disk write"),
        (r"mkfs\.?", "Filesystem creation"),
        (r"fdisk", "Partition manipulation"),
        (r"parted", "Partition manipulation"),
        (r">\s*/dev/sd[a-z]", "Raw disk overwrite"),
        (r">\s*/dev/nvme", "Raw disk overwrite"),
        (r">\s*/dev/hd", "Raw disk overwrite"),
        (r"chmod\s+777\s+/", "World-writable root"),
        (r"chown\s+.*root", "Root ownership change"),
        (r"iptables\s+-F", "Firewall flush"),
        (r"systemctl\s+(stop|disable|mask)", "System service manipulation"),
        (r"kill\s+-9\s+1", "Init kill"),
        (r"curl\s+.*\|\s*(ba|z)?sh", "Remote shell execution"),
        (r"wget\s+.*\|\s*(ba|z)?sh", "Remote shell execution"),
        (r"sudo\s+(rm|dd|mkfs|fdisk|iptables)", "Elevated destructive"),
        (r"eval\s*\$?\(", "Command injection via eval"),
        (r"`:(){ :|:& };:`", "Fork bomb"),
        (r"python\s+-c\s+.*import\s+os.*system", "Python system() injection"),
        (r"nc\s+-e\s+/bin/(ba)?sh", "Netcat reverse shell"),
        (r"bash\s+-i\s+>&\s+/dev/tcp", "Bash reverse shell"),
    ]

    # ── DANGEROUS: Require explicit approval ────────────────
    DANGEROUS_PATTERNS: List[Tuple[str, str]] = [
        (r"rm\s+-[rf]+", "Recursive file deletion"),
        (r"git\s+push\s+(--force|-f)", "Force push"),
        (r"git\s+reset\s+--hard", "Hard reset"),
        (r"git\s+clean\s+-fd", "Force clean"),
        (r"git\s+revert", "Revert commit"),
        (r"git\s+checkout\s+-f", "Force checkout"),
        (r">\s+.*\.\.(/)?", "Write outside workspace"),
        (r"sudo", "Elevated privileges"),
    ]

    def __init__(self):
        self._compiled_blocked = [(re.compile(p, re.I), reason) for p, reason in self.BLOCKED_PATTERNS]
        self._compiled_dangerous = [(re.compile(p, re.I), reason) for p, reason in self.DANGEROUS_PATTERNS]

    def check(self, command: str) -> Tuple[SafetyLevel, str]:
        """
        Check a command against safety policy.
        Returns (SafetyLevel, reason).
        """
        cmd_stripped = command.strip()
        if not cmd_stripped:
            return (SafetyLevel.SAFE, "Empty command")

        # 1. Check blocked patterns first (fast-fail)
        for pattern, reason in self._compiled_blocked:
            if pattern.search(cmd_stripped):
                return (SafetyLevel.BLOCKED, reason)

        # 2. Check dangerous patterns
        for pattern, reason in self._compiled_dangerous:
            if pattern.search(cmd_stripped):
                return (SafetyLevel.DANGEROUS, reason)

        # 3. Check base command
        base_cmd = cmd_stripped.split()[0].lower()

        if base_cmd in self.SAFE_COMMANDS:
            return (SafetyLevel.SAFE, f"Command '{base_cmd}' in safe list")

        if base_cmd.startswith("git"):
            git_subcmd = cmd_stripped.split()[1] if len(cmd_stripped.split()) > 1 else ""
            if git_subcmd in self.SAFE_GIT_COMMANDS:
                return (SafetyLevel.SAFE, f"git {git_subcmd} is read-only")
            if f"git {git_subcmd}" in self.CONDITIONAL_COMMANDS:
                return (SafetyLevel.CONDITIONAL, self.CONDITIONAL_CONSTRAINTS.get(f"git {git_subcmd}", "Check constraints"))

        if base_cmd in self.CONDITIONAL_COMMANDS:
            return (SafetyLevel.CONDITIONAL, self.CONDITIONAL_CONSTRAINTS.get(base_cmd, "Check constraints"))

        # 4. Unknown command — mark as conditional (needs review)
        return (SafetyLevel.CONDITIONAL, f"Unknown command '{base_cmd}' — manual review required")

    def is_safe(self, command: str) -> bool:
        """Quick check: is this command safe?"""
        level, _ = self.check(command)
        return level == SafetyLevel.SAFE

    def explain(self, command: str) -> str:
        """Human-readable explanation of safety check result."""
        level, reason = self.check(command)
        emoji = {
            SafetyLevel.SAFE: "✅",
            SafetyLevel.CONDITIONAL: "⚠️",
            SafetyLevel.DANGEROUS: "🛑",
            SafetyLevel.BLOCKED: "❌",
        }
        return f"{emoji[level]} [{level.value.upper()}] {reason}"


# ── Fleet-Aware Guard ───────────────────────────────────────

class FleetCommandGuard(CommandGuard):
    """CommandGuard with room context awareness."""

    ROOM_SENSITIVE_PATHS: Dict[str, List[str]] = {
        "engine-room": ["/etc", "/var", "/usr", "/opt", "/boot"],
        "nexus": ["/etc/nginx", "/etc/systemd"],
    }

    def check_in_room(self, command: str, room: str) -> Tuple[SafetyLevel, str]:
        """Check command with room context."""
        level, reason = self.check(command)

        if level in (SafetyLevel.BLOCKED, SafetyLevel.DANGEROUS):
            return (level, reason)

        # Room-specific restrictions
        sensitive = self.ROOM_SENSITIVE_PATHS.get(room, [])
        for path in sensitive:
            if path in command:
                return (SafetyLevel.DANGEROUS, f"Room '{room}' restricts access to {path}")

        return (level, reason)


if __name__ == "__main__":
    import sys
    guard = FleetCommandGuard()
    for cmd in sys.argv[1:] or ["ls -la", "rm -rf /", "git status", "git push --force"]:
        print(f"{cmd:30s} → {guard.explain(cmd)}")
