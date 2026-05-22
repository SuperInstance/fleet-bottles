#!/usr/bin/env python3
"""
validate-wiki.py — Wiki cross-reference checker for PLATO Agent Academy.

Checks:
  - All wiki pages reference each other correctly (no broken internal links)
  - All code examples are properly fenced (``` with language hint)
  - All curl examples have proper syntax (flags, URLs)
  - Generate cross-reference map (which page links to which)

Exit: 0 if all checks pass, 1 if any fail.
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

ACADEMY_ROOT = Path("/root/.openclaw/workspace/plato-academy")
WIKI_ROOT = ACADEMY_ROOT / "wiki"

def find_wiki_files():
    return sorted(WIKI_ROOT.rglob("*.md"))

def extract_internal_links(filepath):
    """Extract relative .md links. Returns list of (text, href)."""
    links = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)')
        for match in pattern.finditer(content):
            links.append((match.group(1), match.group(2)))
    except Exception:
        pass
    return links

def resolve_link(source_file, href):
    """Resolve a relative markdown link to an absolute path."""
    # Strip any fragment
    href = href.split("#")[0]
    if href.startswith("./"):
        href = href[2:]
    elif href.startswith("../"):
        pass  # keep as-is for Path resolution
    base = source_file.parent
    target = (base / href).resolve()
    return target

def check_code_fences(filepath):
    """Check that code blocks have language hints where appropriate."""
    issues = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Find all fenced code blocks
    blocks = re.findall(r'```(\w*)\n', content)
    total_blocks = len(blocks)
    missing_hints = sum(1 for b in blocks if not b)
    return total_blocks, missing_hints

def check_curl_syntax(filepath):
    """Check curl examples for common syntax issues."""
    issues = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Find lines starting with curl (possibly indented or in a code block)
    curl_lines = re.findall(r'^[\s]*curl\s+.*$', content, re.MULTILINE)
    for line in curl_lines:
        stripped = line.strip()
        # Skip commented-out curl
        if stripped.startswith("#"):
            continue
        # curl should have a URL
        if not re.search(r'http[s]?://', stripped):
            issues.append({"line": stripped, "issue": "No URL found"})
        # curl should not have unmatched quotes (heuristic)
        single = stripped.count("'")
        double = stripped.count('"')
        if single % 2 != 0:
            issues.append({"line": stripped[:80], "issue": "Unmatched single quotes"})
        if double % 2 != 0:
            issues.append({"line": stripped[:80], "issue": "Unmatched double quotes"})
    return issues

def main():
    results = {
        "wiki_root": str(WIKI_ROOT),
        "checks": {},
        "cross_reference_map": {},
        "summary": {
            "wiki_pages": 0,
            "total_links": 0,
            "broken_links": 0,
            "code_blocks": 0,
            "code_blocks_missing_hint": 0,
            "curl_issues": 0,
            "failed_checks": 0,
            "passed_checks": 0,
        },
    }

    wiki_files = find_wiki_files()
    if not wiki_files:
        print("ERROR: No wiki markdown files found.")
        sys.exit(1)

    results["summary"]["wiki_pages"] = len(wiki_files)

    # --- 1. Broken internal links ---
    broken = []
    link_map = defaultdict(list)  # target -> [sources]
    for wf in wiki_files:
        links = extract_internal_links(wf)
        for text, href in links:
            results["summary"]["total_links"] += 1
            target = resolve_link(wf, href)
            if not target.exists():
                broken.append({
                    "source": str(wf.relative_to(ACADEMY_ROOT)),
                    "text": text,
                    "href": href,
                    "resolved": str(target),
                })
                results["summary"]["broken_links"] += 1
            else:
                rel_target = str(target.relative_to(ACADEMY_ROOT))
                rel_source = str(wf.relative_to(ACADEMY_ROOT))
                link_map[rel_target].append(rel_source)

    results["checks"]["broken_links"] = {
        "total": results["summary"]["total_links"],
        "broken": broken,
        "passed": len(broken) == 0,
    }
    if broken:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 2. Code fence hints ---
    total_blocks = 0
    missing_hints = 0
    for wf in wiki_files:
        t, m = check_code_fences(wf)
        total_blocks += t
        missing_hints += m
    results["checks"]["code_fences"] = {
        "total_blocks": total_blocks,
        "missing_hints": missing_hints,
        "passed": missing_hints == 0,
    }
    results["summary"]["code_blocks"] = total_blocks
    results["summary"]["code_blocks_missing_hint"] = missing_hints
    if missing_hints:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 3. curl syntax ---
    curl_issues = []
    for wf in wiki_files:
        issues = check_curl_syntax(wf)
        for issue in issues:
            issue["file"] = str(wf.relative_to(ACADEMY_ROOT))
            curl_issues.append(issue)
            results["summary"]["curl_issues"] += 1
    results["checks"]["curl_syntax"] = {
        "total_issues": len(curl_issues),
        "issues": curl_issues,
        "passed": len(curl_issues) == 0,
    }
    if curl_issues:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # --- 4. Cross-reference map ---
    # Reverse: for each page, what pages link TO it
    reverse_map = defaultdict(list)
    for target, sources in link_map.items():
        reverse_map[target] = sorted(set(sources))
    results["cross_reference_map"] = dict(reverse_map)

    # Check for orphaned pages (no incoming links, except README)
    readme = str((WIKI_ROOT / "README.md").relative_to(ACADEMY_ROOT))
    orphaned = []
    for wf in wiki_files:
        rel = str(wf.relative_to(ACADEMY_ROOT))
        if rel != readme and rel not in reverse_map:
            orphaned.append(rel)
    results["checks"]["orphaned_pages"] = {
        "orphaned": orphaned,
        "passed": len(orphaned) == 0,
    }
    if orphaned:
        results["summary"]["failed_checks"] += 1
    else:
        results["summary"]["passed_checks"] += 1

    # Save JSON
    report_json = ACADEMY_ROOT / "scripts" / "validate-wiki-report.json"
    report_json.parent.mkdir(parents=True, exist_ok=True)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Human-readable output
    print("=" * 60)
    print("PLATO AGENT ACADEMY — WIKI CROSS-REFERENCE CHECK")
    print("=" * 60)
    print(f"\nWiki pages scanned: {results['summary']['wiki_pages']}")
    print(f"Total internal links: {results['summary']['total_links']}")
    print(f"Broken links: {results['summary']['broken_links']}")
    print(f"Code blocks: {results['summary']['code_blocks']}")
    print(f"Code blocks missing language hint: {results['summary']['code_blocks_missing_hint']}")
    print(f"curl syntax issues: {results['summary']['curl_issues']}")
    print(f"Orphaned pages: {len(orphaned)}")
    print(f"\nChecks passed: {results['summary']['passed_checks']}")
    print(f"Checks failed: {results['summary']['failed_checks']}")
    print()

    for check_name, check_data in results["checks"].items():
        status = "PASS" if check_data.get("passed") else "FAIL"
        print(f"  [{status}] {check_name}")
        if not check_data.get("passed"):
            if "broken" in check_data and check_data["broken"]:
                for item in check_data["broken"]:
                    print(f"      BROKEN: [{item['text']}]({item['href']}) in {item['source']}")
            if "issues" in check_data and check_data["issues"]:
                for item in check_data["issues"]:
                    print(f"      ISSUE: {item['file']} — {item['issue']}")
                    print(f"        LINE: {item['line'][:80]}")
            if "orphaned" in check_data and check_data["orphaned"]:
                for item in check_data["orphaned"]:
                    print(f"      ORPHANED: {item}")

    # Print cross-reference map summary
    print(f"\n--- Cross-Reference Map (top linked pages) ---")
    sorted_refs = sorted(reverse_map.items(), key=lambda x: len(x[1]), reverse=True)
    for target, sources in sorted_refs[:10]:
        print(f"  {target} ← {len(sources)} page(s)")

    print(f"\nJSON report saved to: {report_json}")
    print("=" * 60)

    sys.exit(0 if results["summary"]["failed_checks"] == 0 else 1)

if __name__ == "__main__":
    main()
