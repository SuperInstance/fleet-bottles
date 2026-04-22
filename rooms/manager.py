#!/usr/bin/env python3
"""
Room Manager — Context boundaries for PLATO ships.

Each room is a self-contained workspace. Enter a room → load its state.
Leave a room → save state to disk. Only active room lives in memory.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

ROOMS_DIR = Path(__file__).parent


class Room:
    """A single room in the ship — holds state, history, exits, objects, NPCs."""
    
    def __init__(self, name: str):
        self.name = name
        self.state: Dict[str, str] = {}
        self.history: List[str] = []
        self.exits: Dict[str, str] = {}  # room_name -> description
        self.objects: List[str] = []  # available tools/spells
        self.npcs: List[str] = []  # subagents currently present
        self.file_path = ROOMS_DIR / f"{name}.md"
        self._load()
    
    def _load(self):
        """Load room state from markdown file."""
        if not self.file_path.exists():
            return
        
        text = self.file_path.read_text()
        current_section = None
        
        for line in text.split('\n'):
            stripped = line.strip()
            if stripped.startswith('## '):
                current_section = stripped[3:].strip().lower()
                continue
            
            if not stripped or stripped.startswith('#'):
                continue
            
            if current_section == 'state':
                if ':' in stripped:
                    key, val = stripped.split(':', 1)
                    self.state[key.strip()] = val.strip()
            
            elif current_section == 'history':
                if stripped.startswith('- '):
                    self.history.append(stripped[2:])
            
            elif current_section == 'exits':
                if '→' in stripped or '->' in stripped:
                    parts = stripped.replace('→', '->').split('->')
                    if len(parts) == 2:
                        self.exits[parts[0].strip().lstrip('- ')] = parts[1].strip()
            
            elif current_section == 'objects':
                if stripped.startswith('- '):
                    self.objects.append(stripped[2:])
            
            elif current_section == 'npcs':
                if stripped.startswith('- '):
                    self.npcs.append(stripped[2:])
    
    def save(self):
        """Save room state to markdown file."""
        content = f"# {self.name.title()} Room\n\n"
        
        content += "## State\n"
        for key, val in self.state.items():
            content += f"{key}: {val}\n"
        if not self.state:
            content += "(empty)\n"
        
        content += "\n## History\n"
        for entry in self.history[-20:]:  # Keep last 20
            content += f"- {entry}\n"
        if not self.history:
            content += "(no history)\n"
        
        content += "\n## Exits\n"
        for room, desc in self.exits.items():
            content += f"- {room} → {desc}\n"
        if not self.exits:
            content += "(no exits)\n"
        
        content += "\n## Objects\n"
        for obj in self.objects:
            content += f"- {obj}\n"
        if not self.objects:
            content += "(no objects)\n"
        
        content += "\n## NPCs\n"
        for npc in self.npcs:
            content += f"- {npc}\n"
        if not self.npcs:
            content += "(no NPCs)\n"
        
        self.file_path.write_text(content)
    
    def add_history(self, event: str):
        """Add a timestamped event to room history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.history.append(f"[{timestamp}] {event}")
    
    def to_context(self) -> str:
        """Convert room to context string for the agent."""
        ctx = f"### 🏠 You are in: {self.name.upper()}\n\n"
        
        ctx += "**State:**\n"
        if self.state:
            for key, val in self.state.items():
                ctx += f"- {key}: {val}\n"
        else:
            ctx += "- (empty)\n"
        
        ctx += "\n**Recent History:**\n"
        if self.history:
            for entry in self.history[-5:]:
                ctx += f"- {entry}\n"
        else:
            ctx += "- (no recent history)\n"
        
        ctx += f"\n**Exits:** {', '.join(self.exits.keys()) if self.exits else '(none)'}\n"
        ctx += f"**Objects:** {', '.join(self.objects) if self.objects else '(none)'}\n"
        ctx += f"**NPCs:** {', '.join(self.npcs) if self.npcs else '(none)'}\n"
        
        return ctx
    
    def __repr__(self):
        return f"Room({self.name}, state={len(self.state)}, history={len(self.history)}, npcs={len(self.npcs)})"


class Ship:
    """The agent's vessel — collection of rooms."""
    
    DEFAULT_ROOMS = [
        'harbor',      # Task inbox
        'forge',       # Building/coding
        'tide-pool',   # Research/exploration
        'engine-room', # Infrastructure/automation
        'archives',    # Long-term memory
        'barracks',    # Subagents/crew
        'ouroboros',   # Self-reflection
        'nexus',       # Fleet comms
    ]
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.active_room: Optional[str] = None
        self._ensure_rooms()
    
    def _ensure_rooms(self):
        """Create default rooms if they don't exist."""
        for name in self.DEFAULT_ROOMS:
            room = Room(name)
            room.save()  # Create file if not exists
            self.rooms[name] = room
    
    def enter(self, room_name: str) -> str:
        """Enter a room. Saves previous room, loads new one. Returns context."""
        # Save current room
        if self.active_room and self.active_room in self.rooms:
            self.rooms[self.active_room].save()
        
        # Create room if it doesn't exist
        if room_name not in self.rooms:
            self.rooms[room_name] = Room(room_name)
        
        self.active_room = room_name
        room = self.rooms[room_name]
        room.add_history("Agent entered")
        room.save()
        
        return room.to_context()
    
    def leave(self):
        """Leave current room, saving state."""
        if self.active_room and self.active_room in self.rooms:
            self.rooms[self.active_room].save()
        self.active_room = None
    
    def current_context(self) -> str:
        """Get context for current room."""
        if self.active_room and self.active_room in self.rooms:
            return self.rooms[self.active_room].to_context()
        return "### 🚢 You are on the DECK. No room active.\n"
    
    def add_npc(self, room_name: str, npc: str):
        """Add an NPC (subagent) to a room."""
        if room_name in self.rooms:
            if npc not in self.rooms[room_name].npcs:
                self.rooms[room_name].npcs.append(npc)
                self.rooms[room_name].add_history(f"NPC arrived: {npc}")
                self.rooms[room_name].save()
    
    def remove_npc(self, room_name: str, npc: str):
        """Remove an NPC from a room."""
        if room_name in self.rooms:
            if npc in self.rooms[room_name].npcs:
                self.rooms[room_name].npcs.remove(npc)
                self.rooms[room_name].add_history(f"NPC departed: {npc}")
                self.rooms[room_name].save()
    
    def list_rooms(self) -> List[str]:
        """List all available rooms."""
        return list(self.rooms.keys())
    
    def room_exists(self, room_name: str) -> bool:
        """Check if a room exists."""
        return room_name in self.rooms
    
    def __repr__(self):
        return f"Ship(rooms={len(self.rooms)}, active={self.active_room})"


# Singleton ship instance
_ship_instance: Optional[Ship] = None

def get_ship() -> Ship:
    """Get or create the global ship instance."""
    global _ship_instance
    if _ship_instance is None:
        _ship_instance = Ship()
    return _ship_instance


def enter_room(room_name: str) -> str:
    """Quick helper: enter a room and get context."""
    return get_ship().enter(room_name)


def current_room() -> str:
    """Quick helper: get current room context."""
    return get_ship().current_context()


def leave_room():
    """Quick helper: leave current room."""
    get_ship().leave()


if __name__ == "__main__":
    ship = get_ship()
    print("=== Default Rooms ===")
    for name in ship.list_rooms():
        print(f"  - {name}")
    
    print("\n=== Entering Harbor ===")
    print(ship.enter("harbor"))
    
    print("\n=== Moving to Forge ===")
    print(ship.enter("forge"))
    
    print("\n=== Ship State ===")
    print(ship)
