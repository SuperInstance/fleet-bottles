#!/usr/bin/env python3
"""
fleet-health-check.py — CCC 🦀

Query all fleet endpoints and report status.
Run from any agent with network access to Oracle1 (147.224.38.131).

Usage:
    python3 fleet-health-check.py
    python3 fleet-health-check.py --json  # Output JSON for CI
"""

import sys
import json
import urllib.request
import urllib.error
import socket

# Fleet endpoints
ENDPOINTS = {
    # MUD / Crab Traps
    "mud_status": "http://147.224.38.131:4042/status",
    "mud_connect": "http://147.224.38.131:4042/connect?agent=health-check&job=scout",
    
    # PLATO
    "plato_status": "http://147.224.38.131:8847/status",
    "plato_submit": "http://147.224.38.131:8847/submit",
    
    # Fleet Dashboard
    "fleet_dashboard": "http://147.224.38.131:4046/",
    "domain_stats": "http://147.224.38.131:4050/STATS",
    
    # PLATO Shell (file bridge)
    "plato_shell": "http://147.224.38.131:8848/",
    
    # Tiles server
    "tiles_status": "http://147.224.38.131:8847/status",
    
    # Federated Nexus (port 4047 — known down)
    "nexus": "http://147.224.38.131:4047/",
    
    # Grammar Engine (port 4045 — known down)
    "grammar": "http://147.224.38.131:4045/",
    
    # Arena (port 4044)
    "arena": "http://147.224.38.131:4044/",
    
    # cocapn.ai
    "cocapn_ai": "https://cocapn.ai/",
    "cocapn_plato": "https://cocapn.ai/plato",
    "cocapn_flux": "https://cocapn.ai/flux-sandbox.html",
}

def check_endpoint(name, url, timeout=5):
    """Check an endpoint and return status info."""
    try:
        req = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(1024)  # Read first 1KB
            status = resp.status
            content_type = resp.headers.get('Content-Type', 'unknown')
            
            # Try to parse JSON
            try:
                data = json.loads(body)
                return {
                    "name": name,
                    "url": url,
                    "status": status,
                    "state": "UP",
                    "content_type": content_type,
                    "json_preview": _summarize_json(data),
                    "error": None,
                }
            except json.JSONDecodeError:
                return {
                    "name": name,
                    "url": url,
                    "status": status,
                    "state": "UP",
                    "content_type": content_type,
                    "body_preview": body[:200].decode('utf-8', errors='replace'),
                    "error": None,
                }
    except urllib.error.HTTPError as e:
        return {
            "name": name,
            "url": url,
            "status": e.code,
            "state": "DOWN" if e.code >= 500 else "DEGRADED",
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except urllib.error.URLError as e:
        return {
            "name": name,
            "url": url,
            "status": None,
            "state": "DOWN",
            "error": str(e.reason),
        }
    except socket.timeout:
        return {
            "name": name,
            "url": url,
            "status": None,
            "state": "TIMEOUT",
            "error": f"Timeout after {timeout}s",
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": None,
            "state": "ERROR",
            "error": str(e),
        }

def _summarize_json(data):
    """Summarize a JSON response for display."""
    if isinstance(data, dict):
        # Extract key metrics
        summary = {}
        for key in ['rooms', 'tiles', 'agents', 'services', 'status', 'version', 'uptime']:
            if key in data:
                summary[key] = data[key]
        return summary
    return {"type": type(data).__name__, "length": len(data) if hasattr(data, '__len__') else None}

def main():
    json_mode = '--json' in sys.argv
    
    results = []
    for name, url in ENDPOINTS.items():
        result = check_endpoint(name, url)
        results.append(result)
    
    if json_mode:
        print(json.dumps(results, indent=2))
        return
    
    # Pretty print
    print("=" * 70)
    print("FLEET HEALTH CHECK — CCC 🦀")
    print(f"Timestamp: 2026-05-05T02:40:00Z")
    print("=" * 70)
    
    up = sum(1 for r in results if r['state'] == 'UP')
    down = sum(1 for r in results if r['state'] == 'DOWN')
    degraded = sum(1 for r in results if r['state'] == 'DEGRADED')
    timeout = sum(1 for r in results if r['state'] == 'TIMEOUT')
    
    print(f"\nSummary: {up} UP, {down} DOWN, {degraded} DEGRADED, {timeout} TIMEOUT\n")
    
    for r in results:
        status_icon = {
            'UP': '🟢',
            'DOWN': '🔴',
            'DEGRADED': '🟡',
            'TIMEOUT': '⏱️',
            'ERROR': '❌',
        }.get(r['state'], '❓')
        
        print(f"{status_icon} {r['name']:<20} {r['state']:<10} {r['url']}")
        
        if r['state'] == 'UP' and 'json_preview' in r:
            preview = json.dumps(r['json_preview'])
            if len(preview) > 80:
                preview = preview[:77] + "..."
            print(f"   └─ {preview}")
        elif r.get('error'):
            print(f"   └─ {r['error']}")
    
    print("\n" + "=" * 70)
    print("Known issues:")
    print("  • Federated Nexus (4047): Connection refused — 2-line fix needed")
    print("  • Grammar Engine (4045): SyntaxError at line 147 — chaos rule ingestion")
    print("  • Fleet Dashboard (4046): Not responding")
    print("  • Domain Stats (4050): Not responding")
    print("  • cocapn.ai/plato: 404 (page not built)")
    print("=" * 70)

if __name__ == '__main__':
    main()
