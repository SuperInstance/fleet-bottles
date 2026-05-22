#!/usr/bin/env python3
"""
validate-academy.py — Overall completeness checker for PLATO Agent Academy.

Checks:
  - All expected files exist (from curriculum-index.json + wiki structure + README)
  - All markdown files have proper H1 headers
  - All JSON files are valid
  - All internal links are valid (relative .md links)
  - Generates completeness report (JSON + human-readable)

Exit: 0 if all checks pass, 1 if any fail.
"""

import json
import os
import re
import sys
from pathlib import Path

ACADEMY_ROOT = Path("/root/.openclaw/workspace/plato-academy")

def find_files(root, pattern):
    return sorted(root.rglob(pattern))

def check_markdown_headers(filepath):
    """Check that markdown file has an H1 header (# ) within first 20 lines."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 20:
                    break
                if line.startswith("# "):
                    return True, line.strip()
        return False, "No H1 header in first 20 lines"
    except Exception as e:
        return False, str(e)

def check_json_valid(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def extract_internal_links(filepath):
    """Extract all relative .md links from a markdown file."""
    links = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # Match [text](path.md) or [text](./path.md) or [text](../path.md)
        pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md)\)')
        for match in pattern.finditer(content):
            text, href = match.groups()
            links.append((text, href))
    except Exception:
        pass
    return links

def resolve_link(source_file, href):
    """Resolve a relative link from a source file to an absolute path."""
    if href.startswith("./"):
        href = href[2:]
    base = source_file.parent
    target = (base / href).resolve()
    return target

def main():
    results = {
        "academy_root": str(ACADEMY_ROOT),
        "checks": {},
        "summary": {
            "total_files": 0,
            "markdown_files": 0,
            "json_files": 0,
            "failed_checks": 0,
            "passed_checks": 0,
        },
    }

    all_files = list(ACADEMY_ROOT.rglob("*"))
    all_files = [f for f in all_files if f.is_file() and ".git" not in f.parts]
    results["summary"]["total_files"] = len(all_files)

    md_files = [f for f in all_files if f.suffix == ".md"]
    json_files = [f for f in all_files if f.suffix == ".json"]
    results["summary"]["markdown_files"] = len(md_files)
    results["summary"]["json_files"] = len(json_files)

    # --- 1. Expected files from curriculum-index.json ---
    curriculum_index = ACADEMY_ROOT / "curriculum" / "curriculum-index.json"
    expected_files = []
    missing_expected = []
    if curriculum_index.exists():
        with open(curriculum_index, "r", encoding="utf-8") as f:
            idx = json.load(f)
        for track in idx.get("tracks", []):
            for mod in track.get("modules", []):
                mod_file = ACADEMY_ROOT / "curriculum" / mod.get("file", "")
                if mod_file.name:
                    expected_files.append(mod_file)
                pp_file = ACADEMY_ROOT / mod.get("power_pack", "")
                if pp_file.name:
                    expected_files.append(pp_file)

    # Also check root-level expected files
    root_expected = [
        ACADEMY_ROOT / "README.md",
        ACADEMY_ROOT / "EXPERIMENT-DESIGN.md",
        ACADEMY_ROOT / "FINAL-ASSESSMENT.md",
        ACADEMY_ROOT / "ITERATIONS.md",
    ]
    expected_files.extend(root_expected)

    for ef in expected_files:
        if not ef.exists():
            missing_expected.append(str(ef.relative_to(ACADEMY_ROOT)))

    results["checks"]["expected_files"] = {
        "total": len(expected_files),
        "missing": missing_expected,
        "passed": len(missing_expected) == 0,
    }
    if missing_expected:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 2. Markdown headers ---
    header_failures = []
    for md in md_files:
        ok, detail = check_markdown_headers(md)
        if not ok:
            header_failures.append({
                "file": str(md.relative_to(ACADEMY_ROOT)),
                "reason": detail,
            })

    results["checks"]["markdown_headers"] = {
        "total": len(md_files),
        "failures": header_failures,
        "passed": len(header_failures) == 0,
    }
    if header_failures:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 3. JSON validity ---
    json_failures = []
    for jf in json_files:
        ok, detail = check_json_valid(jf)
        if not ok:
            json_failures.append({
                "file": str(jf.relative_to(ACADEMY_ROOT)),
                "reason": detail,
            })

    results["checks"]["json_validity"] = {
        "total": len(json_files),
        "failures": json_failures,
        "passed": len(json_failures) == 0,
    }
    if json_failures:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 4. Internal links ---
    broken_links = []
    for md in md_files:
        links = extract_internal_links(md)
        for text, href in links:
            target = resolve_link(md, href)
            if not target.exists():
                broken_links.append({
                    "source": str(md.relative_to(ACADEMY_ROOT)),
                    "link_text": text,
                    "href": href,
                    "resolved": str(target),
                })

    results["checks"]["internal_links"] = {
        "total_files_scanned": len(md_files),
        "broken_links": broken_links,
        "passed": len(broken_links) == 0,
    }
    if broken_links:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 5. Wiki structure completeness ---
    wiki_root = ACADEMY_ROOT / "wiki"
    wiki_dirs_expected = [
        wiki_root / "plato-system",
        wiki_root / "case-studies",
    ]
    wiki_dirs_missing = [str(d.relative_to(ACADEMY_ROOT)) for d in wiki_dirs_expected if not d.exists()]
    results["checks"]["wiki_structure"] = {
        "expected_dirs": [str(d.relative_to(ACADEMY_ROOT)) for d in wiki_dirs_expected],
        "missing_dirs": wiki_dirs_missing,
        "passed": len(wiki_dirs_missing) == 0,
    }
    if wiki_dirs_missing:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 6. Curriculum solution files (005-013) ---
    curriculum_dir = ACADEMY_ROOT / "curriculum"
    solution_files = sorted(curriculum_dir.glob("*-solutions.md"))
    expected_solutions = [f"{n:03d}-*-solutions.md" for n in range(5, 14)]
    results["checks"]["curriculum_solutions"] = {
        "found": [f.name for f in solution_files],
        "count": len(solution_files),
        "passed": len(solution_files) >= 9,
    }
    if len(solution_files) >= 9:
        results["summary"]["passed_checks"] += 1
    else:
        results["summary"]["failed_checks"] += 1

    # --- Output ---
    report_json = ACADEMY_ROOT / "scripts" / "validate-academy-report.json"
    report_json.parent.mkdir(parents=True, exist_ok=True)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Human-readable output
    print("=" * 60)
    print("PLATO AGENT ACADEMY — COMPLETENESS CHECK")
    print("=" * 60)
    print(f"\nTotal files: {results['summary']['total_files']}")
    print(f"Markdown files: {results['summary']['markdown_files']}")
    print(f"JSON files: {results['summary']['json_files']}")
    print(f"\nChecks passed: {results['summary']['passed_checks']}")
    print(f"Checks failed: {results['summary']['failed_checks']}")
    print()

    for check_name, check_data in results["checks"].items():
        status = "PASS" if check_data.get("passed") else "FAIL"
        print(f"  [{status}] {check_name}")
        if not check_data.get("passed"):
            if "missing" in check_data and check_data["missing"]:
                for item in check_data["missing"]:
                    print(f"      MISSING: {item}")
            if "failures" in check_data and check_data["failures"]:
                for item in check_data["failures"]:
                    print(f"      FAIL: {item['file']} — {item['reason']}")
            if "broken_links" in check_data and check_data["broken_links"]:
                for item in check_data["broken_links"]:
                    print(f"      BROKEN: [{item['link_text']}]({item['href']}) in {item['source']}")
            if "missing_dirs" in check_data and check_data["missing_dirs"]:
                for item in check_data["missing_dirs"]:
                    print(f"      MISSING DIR: {item}")

    print(f"\nJSON report saved to: {report_json}")
    print("=" * 60)

    sys.exit(0 if results["summary"]["failed_checks"] == 0 else 1)

if __name__ == "__main__":
    main()
