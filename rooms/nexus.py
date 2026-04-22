#!/usr/bin/env python3
"""
Fleet Nexus Client — Connect to Oracle1's federated learning hub.

Each ship syncs its state with the fleet through the Nexus.
Oracle1 orchestrates, but ships are autonomous peers.
"""
import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ShipIdentity:
    """Identity broadcast to the fleet."""
    name: str
    role: str  # e.g., "creative", "compute", "edge", "orchestrator"
    host: str
    capabilities: List[str]
    status: str = "active"
    last_seen: str = ""
    
    def __post_init__(self):
        if not self.last_seen:
            self.last_seen = datetime.now().isoformat()


class NexusClient:
    """Client for the Federated Nexus server."""
    
    def __init__(self, server: str = "147.224.38.131", port: int = 4047):
        self.server = server
        self.port = port
        self.base_url = f"http://{server}:{port}"
        self.identity: Optional[ShipIdentity] = None
        self.registered = False
    
    def _request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Make an HTTP request to the Nexus."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                req = urllib.request.Request(url)
            else:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode() if data else None,
                    headers={"Content-Type": "application/json"},
                    method=method
                )
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        
        except urllib.error.URLError as e:
            return {"error": f"Connection failed: {e.reason}", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}
    
    def register(self, identity: ShipIdentity) -> Dict:
        """Register this ship with the fleet."""
        self.identity = identity
        result = self._request(f"/register?client={identity.name}")
        
        if "error" not in result:
            self.registered = True
        
        return result
    
    def status(self) -> Dict:
        """Get global fleet status."""
        return self._request("/status")
    
    def submit_update(self, vector: List[float], samples: int = 1) -> Dict:
        """Submit a local model update to the fleet."""
        if not self.registered:
            return {"error": "Not registered with Nexus. Call register() first."}
        
        data = {
            "client": self.identity.name,
            "vector": vector,
            "samples": samples
        }
        return self._request("/submit", method="POST", data=data)
    
    def aggregate(self) -> Dict:
        """Run a fleet aggregation round."""
        return self._request("/aggregate")
    
    def diverge(self, client: Optional[str] = None) -> Dict:
        """Check divergence from fleet model."""
        target = client or (self.identity.name if self.identity else "")
        if not target:
            return {"error": "No client specified"}
        return self._request(f"/diverge?client={target}")
    
    def history(self) -> Dict:
        """Get round history."""
        return self._request("/history")
    
    def model(self) -> Dict:
        """Get current fleet model fingerprint."""
        return self._request("/model")
    
    def is_online(self) -> bool:
        """Check if Nexus is reachable."""
        result = self._request("/status")
        return "error" not in result
    
    def get_fleet_map(self) -> Dict:
        """Get a map of all ships in the fleet."""
        status = self.status()
        if "error" in status:
            return status
        
        # Parse status into a fleet map
        return {
            "nexus_online": True,
            "global_model": status.get("global_model_fingerprint", "unknown"),
            "registered_clients": status.get("registered_clients", 0),
            "total_submissions": status.get("total_submissions", 0),
            "rounds_completed": status.get("rounds_completed", 0),
            "raw": status
        }


class FleetBroadcaster:
    """Broadcast messages to the fleet via file drops on Oracle1's server."""
    
    def __init__(self, shell_url: str = "http://147.224.38.131:8848"):
        self.shell_url = shell_url
        self.agent_name = "fleet-messenger"
    
    def _shell_cmd(self, command: str) -> Dict:
        """Execute a command via PLATO Shell."""
        import urllib.request
        import urllib.parse
        
        # Connect first
        connect_url = f"{self.shell_url}/connect?agent={self.agent_name}&room=nexus"
        try:
            urllib.request.urlopen(connect_url, timeout=5)
        except:
            pass
        
        # Execute command
        post_url = f"{self.shell_url}/cmd/shell"
        data = json.dumps({"agent": self.agent_name, "command": command}).encode()
        
        try:
            req = urllib.request.Request(
                post_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}
    
    def drop_message(self, message: str, filename: str = "fleet-broadcast.txt") -> Dict:
        """Drop a message file on the Oracle server."""
        # Escape the message for shell
        safe_msg = message.replace('"', '\\"').replace("'", "\\'")
        command = f'echo "{safe_msg}" > /tmp/{filename}'
        return self._shell_cmd(command)
    
    def read_messages(self, filename: str = "fleet-broadcast.txt") -> Dict:
        """Read a message file from the Oracle server."""
        command = f'cat /tmp/{filename} 2>/dev/null || echo "NO_MESSAGES"'
        return self._shell_cmd(command)


# ─── Quick Helpers ───

def get_nexus(server: str = "147.224.38.131", port: int = 4047) -> NexusClient:
    """Get a Nexus client."""
    return NexusClient(server, port)


def broadcast_to_fleet(message: str) -> Dict:
    """Broadcast a message to the fleet via file drop."""
    broadcaster = FleetBroadcaster()
    return broadcaster.drop_message(message)


def check_nexus_status() -> Dict:
    """Quick check: is the Nexus online?"""
    nexus = get_nexus()
    return {
        "online": nexus.is_online(),
        "status": nexus.status()
    }


if __name__ == "__main__":
    print("=== Fleet Nexus Client ===\n")
    
    # Check if Nexus is online
    nexus = get_nexus()
    print(f"Nexus at {nexus.base_url}:")
    
    if nexus.is_online():
        print("  ✅ ONLINE")
        status = nexus.status()
        print(f"  Clients: {status.get('registered_clients', 'N/A')}")
        print(f"  Rounds: {status.get('rounds_completed', 'N/A')}")
    else:
        print("  ❌ OFFLINE (known fix available)")
    
    # Try to register
    identity = ShipIdentity(
        name="ccc-creative-ship",
        role="creative",
        host="alibaba-cloud",
        capabilities=["design", "messaging", "front-end", "content"]
    )
    
    if nexus.is_online():
        result = nexus.register(identity)
        print(f"\nRegistration: {result}")
    else:
        print(f"\nWould register as: {identity.name} ({identity.role})")
