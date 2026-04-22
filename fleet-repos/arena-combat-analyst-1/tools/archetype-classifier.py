#!/usr/bin/env python3
"""
archetype-classifier.py — Classify an agent's play style from actions.

This is a standalone version of the Arena's classification logic,
but with fixes for the "Unknown" bug and better diagnostics.

Usage:
    python archetype-classifier.py action1,action2,action3
    python archetype-classifier.py --file /path/to/matches.jsonl --agent <name>
    python archetype-classifier.py --interactive
"""
import sys, json, argparse
from pathlib import Path
from collections import Counter

DEFAULT_LOG = Path.home() / ".openclaw" / "workspace" / "data" / "self-play-arena" / "matches.jsonl"

ARCHETYPE_NAMES = [
    "Aggressive Explorer",
    "Cautious Hoarder",
    "Social Mimic",
    "Novel Pathfinder",
    "Methodical Analyst",
    "Creative Synthesizer",
]


def classify(actions):
    """Classify an agent's behavior pattern from a list of action strings."""
    # Fix Bug 2: filter out empty strings
    actions = [a.strip() for a in actions if a and a.strip()]
    
    if not actions:
        return "Unknown", {}
    
    n_examine = sum(1 for a in actions if "examine" in a.lower())
    n_create = sum(1 for a in actions if "create" in a.lower())
    n_think = sum(1 for a in actions if "think" in a.lower())
    n_move = sum(1 for a in actions if "move" in a.lower())
    total = len(actions)
    
    # Build ratio diagnostics
    ratios = {
        "examine_ratio": round(n_examine / total, 2),
        "create_ratio": round(n_create / total, 2),
        "think_ratio": round(n_think / total, 2),
        "move_ratio": round(n_move / total, 2),
    }
    
    if n_move / total > 0.5:
        archetype = "Aggressive Explorer"
    elif n_examine / total > 0.5:
        archetype = "Cautious Hoarder"
    elif n_think / total > 0.4:
        archetype = "Methodical Analyst"
    elif n_create / total > 0.3:
        archetype = "Creative Synthesizer"
    elif n_move / total > 0.3 and n_create / total > 0.2:
        archetype = "Novel Pathfinder"
    else:
        archetype = "Social Mimic"
    
    return archetype, ratios


def load_agent_actions(filepath, agent_name):
    """Load all action sequences for an agent from the match log."""
    all_actions = []
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = json.loads(line)
                if m.get("player_a") == agent_name:
                    all_actions.extend(m.get("player_a_actions", []))
                if m.get("player_b") == agent_name:
                    all_actions.extend(m.get("player_b_actions", []))
    except FileNotFoundError:
        print(f"Log file not found: {filepath}")
        sys.exit(1)
    return all_actions


def main():
    parser = argparse.ArgumentParser(description="Classify agent archetype from actions")
    parser.add_argument("actions", nargs="?", help="Comma-separated action list")
    parser.add_argument("--file", type=Path, default=DEFAULT_LOG, help="Path to matches.jsonl")
    parser.add_argument("--agent", help="Classify an agent from the match log")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if args.interactive:
        print("Archetype Classifier — Interactive Mode")
        print("Enter comma-separated actions (or 'quit' to exit):")
        while True:
            try:
                line = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if line.lower() in ("quit", "exit", "q"):
                break
            actions = [a.strip() for a in line.split(",")]
            archetype, ratios = classify(actions)
            print(f"  Archetype: {archetype}")
            print(f"  Ratios:    {ratios}")
            print()
        return

    if args.agent:
        actions = load_agent_actions(args.file, args.agent)
        print(f"Loaded {len(actions)} action(s) for agent '{args.agent}' from {args.file}")
        if not actions:
            print("No actions found. The agent may only have quick-match records (no actions logged).")
            print("This is Bug 2 in the Arena — quick /match doesn't store action sequences.")
            sys.exit(1)
        archetype, ratios = classify(actions)
        print(f"Archetype: {archetype}")
        print(f"Ratios:    {ratios}")
        print(f"Total actions analyzed: {len(actions)}")
        # Show action frequency
        counts = Counter(actions)
        print("Top actions:")
        for action, count in counts.most_common(5):
            print(f"  {action}: {count}")
        return

    if not args.actions:
        print("Usage:")
        print("  archetype-classifier.py action1,action2,action3")
        print("  archetype-classifier.py --agent <name>")
        print("  archetype-classifier.py --interactive")
        sys.exit(1)

    actions = [a.strip() for a in args.actions.split(",")]
    archetype, ratios = classify(actions)
    print(f"Archetype: {archetype}")
    print(f"Ratios:    {ratios}")


if __name__ == "__main__":
    main()
