#!/usr/bin/env python3
"""
Fleet Consciousness Dashboard
A single-file Flask app that displays live PLATO gate telemetry.

Usage:
    pip install flask requests
    python dashboard.py
    # Open http://localhost:5000

Environment:
    PLATO_GATE_URL  - Gate status endpoint (default: http://147.224.38.131:8847/status)
    PORT            - Dashboard port (default: 5000)
"""

import os
import json
import requests
from datetime import datetime, timezone
from flask import Flask, render_template_string

PLATO_GATE_URL = os.environ.get("PLATO_GATE_URL", "http://147.224.38.131:8847/status")
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# HTML Template — Deep abyssal theme, bioluminescent accents
# ═══════════════════════════════════════════════════════════════════════════════
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fleet Consciousness Dashboard</title>
    <style>
        :root {
            --bg-deep: #0a0f1a;
            --bg-surface: #111827;
            --bg-card: #1a2332;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent-cyan: #22d3ee;
            --accent-green: #34d399;
            --accent-amber: #fbbf24;
            --accent-rose: #fb7185;
            --accent-purple: #a78bfa;
            --border: rgba(34, 211, 238, 0.1);
            --glow: rgba(34, 211, 238, 0.15);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-deep);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }
        header h1 {
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.85rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .status-active {
            background: rgba(52, 211, 153, 0.1);
            color: var(--accent-green);
            border: 1px solid rgba(52, 211, 153, 0.2);
        }
        .status-pulse {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px var(--glow);
        }
        .metric-label {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
        }
        .metric-value.cyan { color: var(--accent-cyan); }
        .metric-value.green { color: var(--accent-green); }
        .metric-value.amber { color: var(--accent-amber); }
        .metric-value.rose { color: var(--accent-rose); }
        .metric-sub {
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }
        .section {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .section h2 {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .section h2::before {
            content: '';
            display: inline-block;
            width: 4px; height: 1.1em;
            background: var(--accent-cyan);
            border-radius: 2px;
        }
        .top-rooms-list {
            list-style: none;
        }
        .room-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
        }
        .room-item:last-child { border-bottom: none; }
        .room-name {
            font-weight: 500;
            font-size: 0.9rem;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding-right: 1rem;
        }
        .room-bar-container {
            flex: 2;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .room-bar {
            height: 8px;
            border-radius: 4px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-purple));
            transition: width 0.6s ease;
            min-width: 2px;
        }
        .room-count {
            font-weight: 600;
            font-variant-numeric: tabular-nums;
            color: var(--accent-cyan);
            min-width: 50px;
            text-align: right;
        }
        .gate-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
        }
        .gate-stat {
            text-align: center;
            padding: 1rem;
            background: var(--bg-surface);
            border-radius: 8px;
        }
        .gate-stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
        }
        .gate-stat-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.25rem;
        }
        .reject-reasons {
            margin-top: 1rem;
        }
        .reason-item {
            display: flex;
            justify-content: space-between;
            padding: 0.4rem 0;
            font-size: 0.85rem;
            border-bottom: 1px dashed var(--border);
        }
        .reason-item:last-child { border-bottom: none; }
        .footer {
            text-align: center;
            padding-top: 1.5rem;
            color: var(--text-secondary);
            font-size: 0.75rem;
            border-top: 1px solid var(--border);
        }
        .error-banner {
            background: rgba(251, 113, 133, 0.1);
            border: 1px solid rgba(251, 113, 133, 0.2);
            color: var(--accent-rose);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            display: none;
        }
        .error-banner.visible { display: block; }
        @media (max-width: 640px) {
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .metric-value { font-size: 1.5rem; }
            header h1 { font-size: 1.25rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦀 Fleet Consciousness</h1>
            <span class="status-badge status-active">
                <span class="status-pulse"></span>
                <span id="gate-status">{{ status }}</span>
            </span>
        </header>

        <div class="error-banner" id="error-banner">
            ⚠ Gate connection failed. Showing cached data.
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Tiles</div>
                <div class="metric-value cyan" id="total-tiles">{{ total_tiles }}</div>
                <div class="metric-sub">across all rooms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Rooms</div>
                <div class="metric-value green" id="room-count">{{ room_count }}</div>
                <div class="metric-sub">active knowledge spaces</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Accepted</div>
                <div class="metric-value amber" id="accepted">{{ accepted }}</div>
                <div class="metric-sub">tiles through the gate</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Rejected</div>
                <div class="metric-value rose" id="rejected">{{ rejected }}</div>
                <div class="metric-sub">filtered tiles</div>
            </div>
        </div>

        <div class="section">
            <h2>Top Rooms by Tile Count</h2>
            <ul class="top-rooms-list" id="top-rooms">
                {% for room in top_rooms %}
                <li class="room-item">
                    <span class="room-name">{{ room.name }}</span>
                    <div class="room-bar-container">
                        <div class="room-bar" style="width: {{ room.bar_width }}%"></div>
                        <span class="room-count">{{ room.tile_count }}</span>
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>

        <div class="section">
            <h2>Gate Statistics</h2>
            <div class="gate-stats">
                <div class="gate-stat">
                    <div class="gate-stat-value cyan">{{ accepted }}</div>
                    <div class="gate-stat-label">Accepted</div>
                </div>
                <div class="gate-stat">
                    <div class="gate-stat-value rose">{{ rejected }}</div>
                    <div class="gate-stat-label">Rejected</div>
                </div>
                <div class="gate-stat">
                    <div class="gate-stat-value amber">{{ accept_rate }}%</div>
                    <div class="gate-stat-label">Accept Rate</div>
                </div>
                <div class="gate-stat">
                    <div class="gate-stat-value green">{{ version }}</div>
                    <div class="gate-stat-label">Gate Version</div>
                </div>
            </div>
            {% if reject_reasons %}
            <div class="reject-reasons">
                <h3 style="font-size:0.85rem;color:var(--text-secondary);margin:1rem 0 0.5rem;text-transform:uppercase;letter-spacing:0.05em;">Rejection Reasons</h3>
                {% for reason, count in reject_reasons.items() %}
                <div class="reason-item">
                    <span>{{ reason.replace('_', ' ') }}</span>
                    <span style="font-weight:600;color:var(--accent-rose);">{{ count }}</span>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <div>Gate: {{ gate_url }}</div>
            <div>Last refresh: <span id="last-refresh">{{ last_refresh }}</span> · Auto-refresh: 30s</div>
            <div style="margin-top:0.25rem;color:var(--text-secondary);">
                Fleet Consciousness v1.0 · Cocapn Fleet
            </div>
        </div>
    </div>

    <script>
        const GATE_API = '/api/status';
        let maxTiles = {{ max_tiles }};

        async function refresh() {
            try {
                const res = await fetch(GATE_API);
                if (!res.ok) throw new Error('HTTP ' + res.status);
                const data = await res.json();

                document.getElementById('error-banner').classList.remove('visible');
                document.getElementById('gate-status').textContent = data.status;
                document.getElementById('total-tiles').textContent = data.total_tiles.toLocaleString();
                document.getElementById('room-count').textContent = data.room_count.toLocaleString();
                document.getElementById('accepted').textContent = data.accepted.toLocaleString();
                document.getElementById('rejected').textContent = data.rejected.toLocaleString();
                document.getElementById('last-refresh').textContent = data.last_refresh;

                // Rebuild top rooms
                const list = document.getElementById('top-rooms');
                list.innerHTML = '';
                const m = Math.max(...data.top_rooms.map(r => r.tile_count), 1);
                data.top_rooms.forEach(room => {
                    const li = document.createElement('li');
                    li.className = 'room-item';
                    li.innerHTML = `
                        <span class="room-name">${room.name}</span>
                        <div class="room-bar-container">
                            <div class="room-bar" style="width: ${(room.tile_count / m * 100).toFixed(1)}%"></div>
                            <span class="room-count">${room.tile_count.toLocaleString()}</span>
                        </div>
                    `;
                    list.appendChild(li);
                });
            } catch (err) {
                document.getElementById('error-banner').classList.add('visible');
                console.error('Refresh failed:', err);
            }
        }

        setInterval(refresh, 30000);
    </script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════════════════════
# Data fetching + rendering
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_gate_data():
    """Fetch and normalize PLATO gate status."""
    try:
        resp = requests.get(PLATO_GATE_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        # Return minimal structure on failure so page still renders
        return {
            "status": "offline",
            "version": "unknown",
            "total_tiles": 0,
            "room_count": 0,
            "accepted": 0,
            "rejected": 0,
            "accept_rate": 0,
            "top_rooms": [],
            "reject_reasons": {},
            "gate_url": PLATO_GATE_URL,
            "last_refresh": f"Error: {e}",
            "max_tiles": 1,
        }

    rooms = data.get("rooms", {})
    room_list = [
        {"name": name, "tile_count": info["tile_count"]}
        for name, info in rooms.items()
    ]
    total = sum(r["tile_count"] for r in room_list)
    max_tiles = max((r["tile_count"] for r in room_list), default=1)

    top = sorted(room_list, key=lambda r: r["tile_count"], reverse=True)[:20]
    for r in top:
        r["bar_width"] = (r["tile_count"] / max_tiles * 100) if max_tiles else 0

    gate_stats = data.get("gate_stats", {})
    accepted = gate_stats.get("accepted", 0)
    rejected = gate_stats.get("rejected", 0)
    total_gate = accepted + rejected
    accept_rate = round(accepted / total_gate * 100, 1) if total_gate else 0

    uptime_raw = data.get("uptime", 0)
    uptime_str = "unknown"
    try:
        from datetime import datetime, timezone
        uptime_dt = datetime.fromtimestamp(uptime_raw, tz=timezone.utc)
        uptime_str = uptime_dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        pass

    return {
        "status": data.get("status", "unknown"),
        "version": data.get("version", "unknown"),
        "total_tiles": total,
        "room_count": len(room_list),
        "accepted": accepted,
        "rejected": rejected,
        "accept_rate": accept_rate,
        "top_rooms": top,
        "reject_reasons": gate_stats.get("reasons", {}),
        "gate_url": PLATO_GATE_URL,
        "last_refresh": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "max_tiles": max_tiles,
    }


@app.route("/")
def index():
    ctx = fetch_gate_data()
    return render_template_string(HTML_TEMPLATE, **ctx)


@app.route("/api/status")
def api_status():
    return fetch_gate_data()


if __name__ == "__main__":
    print(f"🦀 Fleet Consciousness Dashboard")
    print(f"   Gate: {PLATO_GATE_URL}")
    print(f"   URL:  http://0.0.0.0:{PORT}/")
    print(f"   API:  http://0.0.0.0:{PORT}/api/status")
    app.run(host="0.0.0.0", port=PORT, debug=False)
