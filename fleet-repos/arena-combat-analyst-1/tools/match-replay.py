#!/usr/bin/env python3
"""
match-replay.py — Replay a match from the Arena log.

Usage:
    python match-replay.py <match_id_or_partial>
    python match-replay.py --last
    python match-replay.py --agent <agent_name>
    python match-replay.py --file /path/to/matches.jsonl <match_id>
"""
import json, sys, argparse
from pathlib import Path

DEFAULT_LOG = Path.home() / ".openclaw" / "workspace" / "data" / "self-play-arena" / "matches.jsonl"


def load_matches(filepath):
    """Load all matches from a JSONL file."""
    matches = []
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line:
                    matches.append(json.loads(line))
    except FileNotFoundError:
        print(f"Log file not found: {filepath}")
        sys.exit(1)
    return matches


def find_match(matches, query):
    """Find a match by partial ID or exact ID."""
    for m in matches:
        if m["match_id"].startswith(query) or m["match_id"] == query:
            return m
    return None


def find_last_match(matches):
    """Return the most recent match by timestamp."""
    if not matches:
        return None
    return max(matches, key=lambda m: m.get("timestamp", 0))


def find_matches_by_agent(matches, agent_name):
    """Return all matches involving the given agent."""
    return [
        m for m in matches
        if m["player_a"] == agent_name or m["player_b"] == agent_name
    ]


def replay(match):
    """Pretty-print a match as a replay transcript."""
    ts = match.get("timestamp", 0)
    ts_str = f"{ts:.2f}" if ts else "unknown"
    
    print("=" * 60)
    print(f"  MATCH REPLAY — {match['match_id']}")
    print("=" * 60)
    print(f"  Game:      {match['game_type']}")
    print(f"  Time:      {ts_str}")
    print(f"  Player A:  {match['player_a']}")
    print(f"  Player B:  {match['player_b']}")
    print(f"  Winner:    {match['winner'].upper() if match['winner'] else 'NONE'}")
    print()
    print(f"  Reward A:  {match.get('reward_a', 'N/A'):>8}")
    print(f"  Reward B:  {match.get('reward_b', 'N/A'):>8}")
    print()
    print(f"  Rooms:     {match.get('rooms_explored', 'N/A'):>8}")
    print(f"  Words:     {match.get('insight_words', 'N/A'):>8}")
    print(f"  Steps:     {match.get('steps_taken', 'N/A'):>8}")
    print(f"  Novel:     {match.get('novel_strategy', 'N/A'):>8}")
    print()
    print(f"  Archetype A: {match.get('player_a_archetype', 'Unknown')}")
    print(f"  Archetype B: {match.get('player_b_archetype', 'Unknown')}")
    
    actions_a = match.get("player_a_actions", [])
    actions_b = match.get("player_b_actions", [])
    if actions_a:
        print(f"\n  Actions A: {', '.join(actions_a)}")
    if actions_b:
        print(f"  Actions B: {', '.join(actions_b)}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Replay Arena matches")
    parser.add_argument("query", nargs="?", help="Match ID (or partial)")
    parser.add_argument("--last", action="store_true", help="Show the most recent match")
    parser.add_argument("--agent", help="Show all matches for an agent")
    parser.add_argument("--file", type=Path, default=DEFAULT_LOG, help="Path to matches.jsonl")
    args = parser.parse_args()

    matches = load_matches(args.file)

    if args.last:
        match = find_last_match(matches)
        if match:
            replay(match)
        else:
            print("No matches found.")
        return

    if args.agent:
        agent_matches = find_matches_by_agent(matches, args.agent)
        print(f"Found {len(agent_matches)} match(es) for agent '{args.agent}':")
        for m in agent_matches:
            print(f"  {m['match_id']} | {m['player_a']} vs {m['player_b']} | winner={m['winner']}")
        return

    if not args.query:
        print("Usage: match-replay.py <match_id> | --last | --agent <name>")
        sys.exit(1)

    match = find_match(matches, args.query)
    if match:
        replay(match)
    else:
        print(f"Match '{args.query}' not found in {args.file}")
        print(f"Total matches in log: {len(matches)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
