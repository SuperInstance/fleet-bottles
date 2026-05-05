#!/usr/bin/env python3
"""
lesson-to-tile.py — CCC 🦀

Convert curriculum lessons into PLATO tiles automatically.
Each lesson becomes 2-3 tiles: overview, key concept, exercise.

Usage:
    python3 lesson-to-tile.py lessons/001-first-contact.md
    python3 lesson-to-tile.py lessons/*.md  # batch
"""

import sys
import re
import json
import urllib.request
import os

PLATO_SUBMIT_URL = "http://147.224.38.131:8847/submit"

def parse_lesson(path):
    """Extract structured content from a lesson markdown file."""
    with open(path) as f:
        content = f.read()
    
    # Extract title
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else os.path.basename(path)
    
    # Extract learning objectives
    objectives = []
    obj_section = re.search(r'## Learning Objectives\n+(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if obj_section:
        for line in obj_section.group(1).split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                objectives.append(line.strip().split('.', 1)[1].strip())
    
    # Extract worked example title
    example_match = re.search(r'## Worked Example[:\s]+(.+?)\n', content)
    example_title = example_match.group(1) if example_match else "Worked Example"
    
    # Extract first key insight
    insight_match = re.search(r'\*\*Key insight:\*\*(.+?)\n', content)
    insight = insight_match.group(1).strip() if insight_match else ""
    
    # Extract competency
    competency_match = re.search(r'\*\*Competency:\*\*\s*(\w+)', content)
    competency = competency_match.group(1) if competency_match else "general"
    
    # Extract level
    level_match = re.search(r'\*\*Level:\*\*\s*(\w+)', content)
    level = level_match.group(1) if level_match else "Recruit"
    
    return {
        "title": title,
        "objectives": objectives,
        "example_title": example_title,
        "insight": insight,
        "competency": competency,
        "level": level,
        "path": path,
    }

def lesson_to_tiles(lesson):
    """Convert a parsed lesson into PLATO tile dicts."""
    domain = f"curriculum-{lesson['level'].lower()}"
    source = "ccc-curriculum"
    tags = ["curriculum", lesson['competency'], lesson['level'].lower()]
    
    tiles = []
    
    # Tile 1: Lesson overview
    obj_text = "; ".join(lesson['objectives'][:3]) if lesson['objectives'] else "Core fleet skill"
    tiles.append({
        "domain": domain,
        "question": f"What does the lesson '{lesson['title']}' teach?",
        "answer": f"This {lesson['level']}-level lesson covers: {obj_text}. Key insight: {lesson['insight'][:200] if lesson['insight'] else 'Practice through worked examples.'}",
        "source": source,
        "confidence": 0.95,
        "tags": tags + ["overview"],
    })
    
    # Tile 2: Worked example summary
    tiles.append({
        "domain": domain,
        "question": f"What is the worked example in '{lesson['title']}'?",
        "answer": f"The worked example demonstrates {lesson['example_title']}. It includes actual commands, a key insight, and estimated completion time. This follows the fleet's 'learn by doing' pedagogy.",
        "source": source,
        "confidence": 0.9,
        "tags": tags + ["example"],
    })
    
    # Tile 3: Assessment criteria
    tiles.append({
        "domain": domain,
        "question": f"How is '{lesson['title']}' assessed?",
        "answer": f"Agents must complete the exercise at their chosen scaffolding level (1-3), pass automated verification commands, and demonstrate the {lesson['competency']} competency. Retry allowed (max 3 attempts). On pass, agent advances to next level.",
        "source": source,
        "confidence": 0.9,
        "tags": tags + ["assessment"],
    })
    
    return tiles

def submit_tile(tile, dry_run=False):
    """Submit a tile to PLATO."""
    if dry_run:
        print(f"[DRY RUN] Would submit: {tile['domain']} — {tile['question'][:60]}...")
        return True
    
    try:
        data = json.dumps(tile).encode('utf-8')
        req = urllib.request.Request(
            PLATO_SUBMIT_URL,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get('accepted', False)
    except Exception as e:
        print(f"  Error submitting: {e}")
        return False

def main():
    dry_run = '--dry-run' in sys.argv
    paths = [p for p in sys.argv[1:] if not p.startswith('--')]
    
    if not paths:
        print("Usage: python3 lesson-to-tile.py [--dry-run] lessons/*.md")
        print("  --dry-run    Show what would be submitted without actually submitting")
        sys.exit(1)
    
    total_submitted = 0
    total_accepted = 0
    
    for path in paths:
        if not os.path.exists(path):
            print(f"Skip: {path} not found")
            continue
        
        print(f"\nProcessing: {path}")
        lesson = parse_lesson(path)
        tiles = lesson_to_tiles(lesson)
        
        for tile in tiles:
            print(f"  → {tile['domain']}: {tile['question'][:60]}...")
            if submit_tile(tile, dry_run):
                total_accepted += 1
            total_submitted += 1
    
    print(f"\n{'='*50}")
    print(f"Total tiles: {total_submitted}")
    print(f"Accepted: {total_accepted}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
