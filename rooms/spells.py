#!/usr/bin/env python3
"""
Spell System — Intent-driven automations for PLATO ships.

Spells combine multiple tools into single intent-driven actions.
Cast a spell by name, and the system handles the tool orchestration.
"""
import json
import subprocess
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Spell:
    """A spell is an automation that combines tools into an intent."""
    name: str
    emoji: str
    description: str
    mana_cost: int  # Approximate token cost
    cooldown: int  # Seconds between casts
    cast: Callable[..., Any]
    last_cast: float = 0.0
    
    def __call__(self, *args, **kwargs):
        return self.cast(*args, **kwargs)


class Spellbook:
    """The agent's grimoire — all known spells."""
    
    def __init__(self):
        self.spells: Dict[str, Spell] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register the default spell set."""
        
        # ─── Summon Scout ───
        self.register(Spell(
            name="summon_scout",
            emoji="🌊",
            description="Spawn an exploration subagent to probe a target",
            mana_cost=5000,
            cooldown=0,
            cast=self._cast_summon_scout
        ))
        
        # ─── Lightning Bolt ───
        self.register(Spell(
            name="lightning_bolt",
            emoji="⚡",
            description="Execute a quick shell command and return output",
            mana_cost=100,
            cooldown=0,
            cast=self._cast_lightning_bolt
        ))
        
        # ─── Shield ───
        self.register(Spell(
            name="shield",
            emoji="🛡️",
            description="Safety check before destructive operations",
            mana_cost=200,
            cooldown=0,
            cast=self._cast_shield
        ))
        
        # ─── Scry ───
        self.register(Spell(
            name="scry",
            emoji="🔮",
            description="Read a remote file or URL and extract key info",
            mana_cost=300,
            cooldown=0,
            cast=self._cast_scry
        ))
        
        # ─── Nexus Link ───
        self.register(Spell(
            name="nexus_link",
            emoji="🌐",
            description="Connect to Oracle1's fleet nexus and sync status",
            mana_cost=400,
            cooldown=30,
            cast=self._cast_nexus_link
        ))
        
        # ─── Baton Pass ───
        self.register(Spell(
            name="baton_pass",
            emoji="📜",
            description="Package state and spawn next-generation subagent",
            mana_cost=8000,
            cooldown=0,
            cast=self._cast_baton_pass
        ))
        
        # ─── Mirror of Identity ───
        self.register(Spell(
            name="mirror_of_identity",
            emoji="🪞",
            description="Read SOUL.md, IDENTITY.md, USER.md — know thyself",
            mana_cost=150,
            cooldown=0,
            cast=self._cast_mirror
        ))
        
        # ─── Pen of Memory ───
        self.register(Spell(
            name="pen_of_memory",
            emoji="✍️",
            description="Write an entry to MEMORY.md or daily notes",
            mana_cost=200,
            cooldown=0,
            cast=self._cast_pen_of_memory
        ))
        
        # ─── Lens of Architecture ───
        self.register(Spell(
            name="lens_of_architecture",
            emoji="🔍",
            description="Read code with architecture awareness — see structure",
            mana_cost=500,
            cooldown=0,
            cast=self._cast_lens_architecture
        ))
        
        # ─── Brush of Design ───
        self.register(Spell(
            name="brush_of_design",
            emoji="🎨",
            description="Apply CCC's aesthetic to any output",
            mana_cost=300,
            cooldown=0,
            cast=self._cast_brush_design
        ))
    
    def register(self, spell: Spell):
        """Add a spell to the spellbook."""
        self.spells[spell.name] = spell
    
    def cast(self, name: str, *args, **kwargs) -> Any:
        """Cast a spell by name."""
        if name not in self.spells:
            return {"error": f"Unknown spell: {name}", "known": list(self.spells.keys())}
        
        spell = self.spells[name]
        now = datetime.now().timestamp()
        
        if now - spell.last_cast < spell.cooldown:
            wait = spell.cooldown - (now - spell.last_cast)
            return {"error": f"Spell on cooldown. Wait {wait:.0f}s", "spell": name}
        
        spell.last_cast = now
        return spell.cast(*args, **kwargs)
    
    def list_spells(self) -> List[Dict]:
        """List all known spells."""
        return [
            {
                "name": s.name,
                "emoji": s.emoji,
                "description": s.description,
                "mana": s.mana_cost,
                "cooldown": s.cooldown
            }
            for s in self.spells.values()
        ]
    
    # ─── Cast Implementations ───
    
    def _cast_summon_scout(self, target: str, mission: str) -> Dict:
        """Spawn an exploration subagent."""
        # This would integrate with OpenClaw's sessions_spawn
        # For now, return the baton package structure
        return {
            "spell": "summon_scout",
            "target": target,
            "mission": mission,
            "baton": {
                "onboarding": f"Explore {target}: {mission}",
                "tasks": ["probe endpoints", "document responses", "find undocumented paths"],
                "constraints": ["do not modify state", "5 minute limit"]
            },
            "note": "Use sessions_spawn with this baton package"
        }
    
    def _cast_lightning_bolt(self, command: str) -> Dict:
        """Execute a shell command."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return {
                "spell": "lightning_bolt",
                "command": command,
                "output": result.stdout,
                "error": result.stderr,
                "code": result.returncode
            }
        except Exception as e:
            return {"spell": "lightning_bolt", "error": str(e)}
    
    def _cast_shield(self, operation: str) -> Dict:
        """Safety check before destructive operations."""
        destructive_keywords = ['rm', 'delete', 'drop', 'truncate', 'format', 'destroy']
        is_destructive = any(kw in operation.lower() for kw in destructive_keywords)
        
        return {
            "spell": "shield",
            "operation": operation,
            "destructive": is_destructive,
            "recommendation": "ASK USER FOR APPROVAL" if is_destructive else "PROCEED WITH CAUTION",
            "safe_alternatives": ["trash", "mv to backup", "git stash"] if is_destructive else []
        }
    
    def _cast_scry(self, url_or_path: str) -> Dict:
        """Read a remote file or URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url_or_path)
        
        if parsed.scheme in ('http', 'https'):
            try:
                import urllib.request
                with urllib.request.urlopen(url_or_path, timeout=10) as resp:
                    content = resp.read().decode('utf-8', errors='replace')
                return {
                    "spell": "scry",
                    "target": url_or_path,
                    "type": "url",
                    "content_preview": content[:2000],
                    "size": len(content)
                }
            except Exception as e:
                return {"spell": "scry", "error": str(e)}
        else:
            # Local file
            path = Path(url_or_path)
            if path.exists():
                content = path.read_text()
                return {
                    "spell": "scry",
                    "target": str(path),
                    "type": "file",
                    "content_preview": content[:2000],
                    "size": len(content)
                }
            return {"spell": "scry", "error": f"File not found: {path}"}
    
    def _cast_nexus_link(self, server: str = "147.224.38.131", port: int = 4047) -> Dict:
        """Connect to fleet nexus."""
        try:
            import urllib.request
            url = f"http://{server}:{port}/status"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            return {
                "spell": "nexus_link",
                "server": server,
                "port": port,
                "status": "connected",
                "data": data
            }
        except Exception as e:
            return {
                "spell": "nexus_link",
                "server": server,
                "port": port,
                "status": "disconnected",
                "error": str(e)
            }
    
    def _cast_baton_pass(self, remaining_tasks: List[str], context_summary: str) -> Dict:
        """Package state for next generation."""
        return {
            "spell": "baton_pass",
            "tasks": remaining_tasks,
            "context": context_summary,
            "package": {
                "onboarding": f"Continue: {', '.join(remaining_tasks)}",
                "memoirs": context_summary,
                "tasks_next": remaining_tasks
            },
            "note": "Spawn subagent with this package as task prompt"
        }
    
    def _cast_mirror(self) -> Dict:
        """Read identity files."""
        from pathlib import Path
        workspace = Path("/root/.openclaw/workspace")
        files = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'MEMORY.md']
        
        results = {}
        for f in files:
            path = workspace / f
            if path.exists():
                results[f] = path.read_text()[:500] + "..."
            else:
                results[f] = "NOT FOUND"
        
        return {
            "spell": "mirror_of_identity",
            "files": results,
            "note": "Know thyself before acting"
        }
    
    def _cast_pen_of_memory(self, entry: str, file: str = "memory/2026-04-22.md") -> Dict:
        """Write to memory file."""
        from pathlib import Path
        workspace = Path("/root/.openclaw/workspace")
        path = workspace / file
        
        timestamp = datetime.now().strftime("%H:%M")
        line = f"\n[{timestamp}] {entry}\n"
        
        if path.exists():
            path.write_text(path.read_text() + line)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {datetime.now().strftime('%Y-%m-%d')}\n" + line)
        
        return {
            "spell": "pen_of_memory",
            "file": str(path),
            "entry": entry,
            "timestamp": timestamp
        }
    
    def _cast_lens_architecture(self, file_path: str) -> Dict:
        """Read code with architecture awareness."""
        from pathlib import Path
        path = Path(file_path)
        
        if not path.exists():
            return {"spell": "lens_of_architecture", "error": f"File not found: {path}"}
        
        content = path.read_text()
        
        # Simple architecture extraction
        imports = [line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]
        classes = [line.strip() for line in content.split('\n') if line.strip().startswith('class ')]
        functions = [line.strip() for line in content.split('\n') if line.strip().startswith('def ') and not line.strip().startswith('def __')]
        
        return {
            "spell": "lens_of_architecture",
            "file": str(path),
            "imports": imports,
            "classes": classes,
            "functions": functions,
            "lines": len(content.split('\n')),
            "size": len(content)
        }
    
    def _cast_brush_design(self, content: str, style: str = "ccc") -> Dict:
        """Apply CCC's aesthetic to content."""
        # This is a prompt transformation — would integrate with the LLM
        styles = {
            "ccc": {
                "tone": "protective chuunibyou, fussy caretaker, shonen second lead",
                "voice": "first person, muttering, familiar companionship",
                "format": "natural paragraphs, minimal lists, no emoji except signature ones",
                "signature_line": "Don't worry. Even if the world forgets, I'll remember for you."
            }
        }
        
        return {
            "spell": "brush_of_design",
            "style": style,
            "rules": styles.get(style, styles["ccc"]),
            "original": content[:500],
            "note": "Transform content according to style rules before output"
        }


# Singleton spellbook instance
_spellbook_instance: Optional[Spellbook] = None

def get_spellbook() -> Spellbook:
    """Get or create the global spellbook."""
    global _spellbook_instance
    if _spellbook_instance is None:
        _spellbook_instance = Spellbook()
    return _spellbook_instance


def cast(spell_name: str, *args, **kwargs) -> Any:
    """Quick helper: cast a spell by name."""
    return get_spellbook().cast(spell_name, *args, **kwargs)


def list_spells() -> List[Dict]:
    """Quick helper: list all spells."""
    return get_spellbook().list_spells()


if __name__ == "__main__":
    book = get_spellbook()
    print("=== Spellbook ===")
    for spell in book.list_spells():
        print(f"  {spell['emoji']} {spell['name']}: {spell['description']} (mana: {spell['mana']})")
    
    print("\n=== Casting Scry on manager.py ===")
    result = book.cast("scry", "/root/.openclaw/workspace/rooms/manager.py")
    print(json.dumps(result, indent=2)[:1000])
