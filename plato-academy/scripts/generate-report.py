#!/usr/bin/env python3
"""
generate-report.py — Academy status report generator for PLATO Agent Academy.

Generates a markdown report suitable for README with:
  - File counts per directory
  - Word/line counts per file
  - Completion percentages
  - Structured JSON metadata alongside

Exit: 0 always (report generator, not validator).
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

ACADEMY_ROOT = Path("/root/.openclaw/workspace/plato-academy")

def count_words_lines(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.count("\n") + 1 if content else 0
        words = len(content.split())
        return words, lines
    except Exception:
        return 0, 0

def main():
    results = {
        "academy_root": str(ACADEMY_ROOT),
        "generated_at": None,
        "directories": {},
        "file_stats": [],
        "completion": {},
        "totals": {
            "files": 0,
            "words": 0,
            "lines": 0,
        },
    }

    all_files = sorted(ACADEMY_ROOT.rglob("*"))
    all_files = [f for f in all_files if f.is_file() and ".git" not in f.parts]

    dir_counts = defaultdict(lambda: {"files": 0, "words": 0, "lines": 0})
    file_stats = []

    for f in all_files:
        words, lines = count_words_lines(f)
        rel = str(f.relative_to(ACADEMY_ROOT))
        parent = str(f.parent.relative_to(ACADEMY_ROOT)) if f.parent != ACADEMY_ROOT else "."
        dir_counts[parent]["files"] += 1
        dir_counts[parent]["words"] += words
        dir_counts[parent]["lines"] += lines
        results["totals"]["files"] += 1
        results["totals"]["words"] += words
        results["totals"]["lines"] += lines
        file_stats.append({
            "file": rel,
            "words": words,
            "lines": lines,
            "size_bytes": f.stat().st_size,
        })

    results["directories"] = dict(dir_counts)
    results["file_stats"] = file_stats

    # --- Completion percentages ---
    # Curriculum: expect 13 modules (1 core + 9 solution files + curriculum-index.json)
    curriculum_dir = ACADEMY_ROOT / "curriculum"
    curriculum_files = list(curriculum_dir.glob("*"))
    curriculum_files = [f for f in curriculum_files if f.is_file()]
    expected_curriculum_files = 13
    results["completion"]["curriculum_files"] = {
        "found": len(curriculum_files),
        "expected": expected_curriculum_files,
        "percent": round(min(100, (len(curriculum_files) / expected_curriculum_files) * 100), 1),
    }

    # Wiki pages
    wiki_files = list((ACADEMY_ROOT / "wiki").rglob("*.md"))
    wiki_files = [f for f in wiki_files if ".git" not in f.parts]
    expected_wiki_pages = 15
    results["completion"]["wiki_pages"] = {
        "found": len(wiki_files),
        "expected": expected_wiki_pages,
        "percent": round(min(100, (len(wiki_files) / expected_wiki_pages) * 100), 1),
    }

    # Power packs
    pp_files = list((ACADEMY_ROOT / "power-packs").rglob("*"))
    pp_files = [f for f in pp_files if f.is_file()]
    expected_pp = 13
    results["completion"]["power_packs"] = {
        "found": len(pp_files),
        "expected": expected_pp,
        "percent": round(min(100, (len(pp_files) / expected_pp) * 100), 1),
    }

    # Overall completion
    weights = {
        "curriculum_files": 0.4,
        "wiki_pages": 0.35,
        "power_packs": 0.25,
    }
    overall = 0
    for key, weight in weights.items():
        overall += results["completion"][key]["percent"] * weight
    results["completion"]["overall"] = round(overall, 1)

    # Save JSON
    json_path = ACADEMY_ROOT / "scripts" / "academy-status-report.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Generate Markdown report
    md_path = ACADEMY_ROOT / "scripts" / "ACADEMY-STATUS.md"
    md_lines = [
        "# PLATO Agent Academy — Status Report",
        "",
        f"> Auto-generated status report for the Cocapn Fleet Agent Academy.",
        f"> Total files: **{results['totals']['files']}** | Total words: **{results['totals']['words']:,}** | Total lines: **{results['totals']['lines']:,}**",
        "",
        "---",
        "",
        "## Completion Summary",
        "",
        "| Component | Found | Expected | Completion |",
        "|-----------|-------|----------|------------|",
    ]
    for key, data in results["completion"].items():
        if key == "overall":
            continue
        label = key.replace("_", " ").title()
        bar = "█" * int(data["percent"] / 5) + "░" * (20 - int(data["percent"] / 5))
        md_lines.append(f"| {label} | {data['found']} | {data['expected']} | {bar} {data['percent']}% |")
    md_lines.append("")
    md_lines.append(f"**Overall Academy Completion: {results['completion']['overall']}%**")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## Files by Directory")
    md_lines.append("")
    md_lines.append("| Directory | Files | Words | Lines |")
    md_lines.append("|-----------|-------|-------|-------|")

    sorted_dirs = sorted(results["directories"].items(), key=lambda x: x[1]["files"], reverse=True)
    for dname, stats in sorted_dirs:
        display = dname if dname != "." else "(root)"
        md_lines.append(f"| {display} | {stats['files']} | {stats['words']:,} | {stats['lines']:,} |")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## Largest Files")
    md_lines.append("")
    md_lines.append("| File | Words | Lines | Size |")
    md_lines.append("|------|-------|-------|------|")
    top_files = sorted(results["file_stats"], key=lambda x: x["words"], reverse=True)[:20]
    for fstat in top_files:
        size_kb = round(fstat["size_bytes"] / 1024, 1)
        md_lines.append(f"| {fstat['file']} | {fstat['words']:,} | {fstat['lines']:,} | {size_kb} KB |")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("## Academy Structure")
    md_lines.append("")
    md_lines.append("```")
    for dname, stats in sorted_dirs:
        display = dname if dname != "." else "."
        md_lines.append(f"{display}/ ({stats['files']} files, {stats['words']:,} words)")
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")
    md_lines.append("*Report generated by `scripts/generate-report.py`'*")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # Print summary to stdout
    print("=" * 60)
    print("PLATO AGENT ACADEMY — STATUS REPORT GENERATED")
    print("=" * 60)
    print(f"\nTotal files: {results['totals']['files']}")
    print(f"Total words: {results['totals']['words']:,}")
    print(f"Total lines: {results['totals']['lines']:,}")
    print(f"\nOverall completion: {results['completion']['overall']}%")
    print()
    for key, data in results["completion"].items():
        if key == "overall":
            continue
        label = key.replace("_", " ").title()
        print(f"  {label}: {data['found']}/{data['expected']} ({data['percent']}%)")
    print()
    print(f"Markdown report: {md_path}")
    print(f"JSON report: {json_path}")
    print("=" * 60)

    sys.exit(0)

if __name__ == "__main__":
    main()
