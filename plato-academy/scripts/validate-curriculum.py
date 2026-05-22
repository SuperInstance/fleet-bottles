#!/usr/bin/env python3
"""
validate-curriculum.py — Curriculum quality checker for PLATO Agent Academy.

Checks every "*-solutions.md" curriculum file for:
  - 4 Trials (A, B, C, D) with code blocks
  - 3 Exercise levels (Recruit / Sailor / Officer)
  - Instructor Notes section
  - Module numbering sequential (005–013)
  - Cross-references between modules
  - Quality score per module (0–100)

Exit: 0 if all checks pass, 1 if any fail.
"""

import json
import os
import re
import sys
from pathlib import Path

ACADEMY_ROOT = Path("/root/.openclaw/workspace/plato-academy")
CURRICULUM_DIR = ACADEMY_ROOT / "curriculum"

def parse_module_file(filepath):
    """Parse a solutions markdown file and extract structural elements."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    result = {
        "filename": filepath.name,
        "title": None,
        "trials": {},
        "exercises": {},
        "has_instructor_notes": False,
        "code_blocks": 0,
        "total_lines": content.count("\n") + 1,
        "word_count": len(content.split()),
    }

    # Extract title from H1
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        result["title"] = m.group(1).strip()

    # Find trials A-D
    for letter in ["A", "B", "C", "D"]:
        pattern = rf'^(##\s+Trial\s+{letter}[^\n]*)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            trial_title = match.group(1)
            # Find code blocks in this trial (between this header and next ##)
            start = match.end()
            next_header = re.search(r'^##\s+', content[start:], re.MULTILINE)
            end = start + next_header.start() if next_header else len(content)
            trial_section = content[start:end]
            code_count = len(re.findall(r'`{3,}[\n\r]*?\n[\s\S]*?`{3,}', trial_section))
            result["trials"][letter] = {
                "title": trial_title,
                "code_blocks": code_count,
            }

    # Find exercises Recruit / Sailor / Officer
    for level in ["Recruit", "Sailor", "Officer"]:
        pattern = rf'^(##\s+Exercise:[^\n]*\({level}\)[^\n]*)$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if not match:
            # Try alternate pattern: "Scaffolding Level N (Recruit)"
            pattern2 = rf'^(##\s+Exercise:[^\n]*\b{level}\b[^\n]*)$'
            match = re.search(pattern2, content, re.MULTILINE | re.IGNORECASE)
        if match:
            result["exercises"][level] = {"title": match.group(1)}

    # Instructor Notes
    if re.search(r'^##\s+Instructor\s+Notes', content, re.MULTILINE | re.IGNORECASE):
        result["has_instructor_notes"] = True

    # Total code blocks
    result["code_blocks"] = len(re.findall(r'`{3,}[\n\r]*?\n[\s\S]*?`{3,}', content))

    return result

def compute_quality_score(parsed):
    """Compute a quality score 0–100 for a module."""
    score = 0
    # 4 trials = 40 points (10 each)
    for letter in ["A", "B", "C", "D"]:
        if letter in parsed["trials"]:
            score += 5
            if parsed["trials"][letter]["code_blocks"] > 0:
                score += 5
    # 3 exercises = 30 points (10 each)
    for level in ["Recruit", "Sailor", "Officer"]:
        if level in parsed["exercises"]:
            score += 10
    # Instructor notes = 15 points
    if parsed["has_instructor_notes"]:
        score += 15
    # Minimum content = 15 points (need >100 lines and >500 words)
    if parsed["total_lines"] >= 100:
        score += 8
    if parsed["word_count"] >= 500:
        score += 7
    return min(100, score)

def main():
    results = {
        "academy_root": str(ACADEMY_ROOT),
        "modules": {},
        "summary": {
            "modules_checked": 0,
            "modules_passing": 0,
            "modules_failing": 0,
            "total_trials": 0,
            "total_exercises": 0,
            "average_quality_score": 0,
        },
    }

    solution_files = sorted(CURRICULUM_DIR.glob("*-solutions.md"))
    if not solution_files:
        print("ERROR: No *-solutions.md files found in curriculum/")
        sys.exit(1)

    all_scores = []
    any_fail = False

    for sf in solution_files:
        parsed = parse_module_file(sf)
        mod_id = sf.stem.split("-")[0]  # e.g. "005" from "005-ci-deployment-solutions"
        score = compute_quality_score(parsed)
        all_scores.append(score)

        # Determine pass/fail per module
        checks = {
            "trial_a": "A" in parsed["trials"] and parsed["trials"]["A"]["code_blocks"] > 0,
            "trial_b": "B" in parsed["trials"] and parsed["trials"]["B"]["code_blocks"] > 0,
            "trial_c": "C" in parsed["trials"] and parsed["trials"]["C"]["code_blocks"] > 0,
            "trial_d": "D" in parsed["trials"] and parsed["trials"]["D"]["code_blocks"] > 0,
            "exercise_recruit": "Recruit" in parsed["exercises"],
            "exercise_sailor": "Sailor" in parsed["exercises"],
            "exercise_officer": "Officer" in parsed["exercises"],
            "instructor_notes": parsed["has_instructor_notes"],
        }
        module_pass = all(checks.values())

        mod_result = {
            "title": parsed["title"],
            "file": str(sf.relative_to(ACADEMY_ROOT)),
            "quality_score": score,
            "checks": checks,
            "trials_found": list(parsed["trials"].keys()),
            "exercises_found": list(parsed["exercises"].keys()),
            "code_blocks": parsed["code_blocks"],
            "word_count": parsed["word_count"],
            "lines": parsed["total_lines"],
            "passed": module_pass,
        }
        results["modules"][mod_id] = mod_result
        results["summary"]["modules_checked"] += 1
        if module_pass:
            results["summary"]["modules_passing"] += 1
        else:
            results["summary"]["modules_failing"] += 1
            any_fail = True

        results["summary"]["total_trials"] += len(parsed["trials"])
        results["summary"]["total_exercises"] += len(parsed["exercises"])

    results["summary"]["average_quality_score"] = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    # Check sequential numbering — we expect 002,003,005-013 (11 modules)
    expected_ids = ["002", "003"] + [f"{n:03d}" for n in range(5, 14)]
    found_ids = sorted(results["modules"].keys())
    missing_ids = [eid for eid in expected_ids if eid not in found_ids]
    results["sequential_check"] = {
        "expected": expected_ids,
        "found": found_ids,
        "missing": missing_ids,
        "passed": len(missing_ids) == 0,
    }
    if missing_ids:
        any_fail = True

    # Cross-references: check if modules reference each other
    cross_refs = {}
    for mod_id, mod_data in results["modules"].items():
        filepath = ACADEMY_ROOT / mod_data["file"]
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        refs_found = []
        for other_id in results["modules"]:
            if other_id != mod_id:
                # Look for references like "Module X", "Lesson XXX", or the module number
                if re.search(rf'\b{other_id}\b', content):
                    refs_found.append(other_id)
        cross_refs[mod_id] = refs_found
    results["cross_references"] = cross_refs

    # Save JSON
    report_json = ACADEMY_ROOT / "scripts" / "validate-curriculum-report.json"
    report_json.parent.mkdir(parents=True, exist_ok=True)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Human-readable output
    print("=" * 60)
    print("PLATO AGENT ACADEMY — CURRICULUM QUALITY CHECK")
    print("=" * 60)
    print(f"\nModules checked: {results['summary']['modules_checked']}")
    print(f"Passing: {results['summary']['modules_passing']}")
    print(f"Failing: {results['summary']['modules_failing']}")
    print(f"Average quality score: {results['summary']['average_quality_score']}/100")
    print(f"Total trials: {results['summary']['total_trials']} (expected: {results['summary']['modules_checked'] * 4})")
    print(f"Total exercises: {results['summary']['total_exercises']} (expected: {results['summary']['modules_checked'] * 3})")
    print()

    for mod_id in sorted(results["modules"].keys()):
        mod = results["modules"][mod_id]
        status = "PASS" if mod["passed"] else "FAIL"
        print(f"  [{status}] {mod_id}: {mod['title']} — Score: {mod['quality_score']}/100")
        if not mod["passed"]:
            for check_name, passed in mod["checks"].items():
                if not passed:
                    print(f"      MISSING: {check_name}")

    if missing_ids:
        print(f"\n  [FAIL] Sequential numbering — missing: {', '.join(missing_ids)}")
    else:
        print(f"\n  [PASS] Sequential numbering 005–013")

    print(f"\nJSON report saved to: {report_json}")
    print("=" * 60)

    sys.exit(0 if not any_fail else 1)

if __name__ == "__main__":
    main()
