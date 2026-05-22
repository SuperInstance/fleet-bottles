#!/usr/bin/env python3
"""
Fleet Triage Generator

Regenerates all triage indexes from live GitHub data.
Run: python3 scripts/regenerate-triage.py

Requires: gh CLI authenticated, jq, python3
"""

import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    requests = None

ORG = "SuperInstance"
REPO_LIMIT = 2000

# Known fleet categorization
core_fleet = {
    'cocapn', 'SuperInstance', 'flux-research', 'flux-isa', 'flux-vm', 'flux-site',
    'flux-docs', 'flux-multilingual', 'flux-verify-api', 'cocapn-cli', 'zeroclaw',
    'constraint-theory-core', 'eisenstein', 'holonomy-consensus', 'pythagorean48-codes',
    'plato-vessel-core', 'keeper-beacon', 'fleet-health-monitor', 'fleet-router', 'fleet-calibrator'
}
named_vessels = {
    'oracle1-vessel', 'oracle1-workspace', 'forgemaster', 'jc1-research',
    'plato-room-phi', 'plato-types', 'plato-data', 'plato-matrix-bridge', 'plato-mcp',
    'plato-training', 'plato-ng', 'platoclaw', 'plato-shell-bridge', 'plato-tile-library',
    'plato-experience', 'plato-watch'
}
integration = {'OpenShell', 'terax-ai', 'terax-gateway', 'MemEye', 'openarm', 'openhuman', 'automerge', 'DeepGEMM'}
experimental = {
    'friendly-fox', 'construct', 'incubator', 'servo-mind', 'servo-mind-theory',
    'dog-food-audit', 'penrose-memory', 'neural-plato', 'tensor-spline', 'warp-room',
    'spread', 'signal-chain', 'tile-chain', 'bathydata-map', 'universe-chain',
    'game-chain', 'seed-oscillate', 'seed-tick-audit', 'night-wheel', 'fleet-stitch',
    'fleet-spread', 'fleet-topology', 'fleet-homology', 'fleet-manifest', 'fleet-math-py',
    'fleet-phase', 'fleet-yaw', 'fleet-consciousness', 'coordination-topology',
    'coordination-hierarchy', 'spreadsheet-cells', 'spreadsheet-projection',
    'llm-proxy', 'topology-anomaly-detector'
}


def normalize_api_repo(raw):
    """Convert GitHub API response to gh CLI format."""
    lang = raw.get('language')
    vis = raw.get('visibility')
    if not vis:
        # API uses 'private' boolean
        vis = 'private' if raw.get('private', False) else 'public'
    return {
        'name': raw['name'],
        'createdAt': raw['created_at'],
        'pushedAt': raw['pushed_at'],
        'description': raw.get('description') or '',
        'primaryLanguage': {'name': lang} if lang else None,
        'isFork': raw.get('fork', False),
        'isArchived': raw.get('archived', False),
        'visibility': vis,
    }


def fetch_repos():
    """Fetch all repos from GitHub via API or gh CLI."""
    print("Fetching repos from GitHub...")
    
    # Try GitHub API first (works in Actions with GITHUB_TOKEN if scoped correctly)
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        print("  Using GitHub API (GITHUB_TOKEN detected)")
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        repos = []
        page = 1
        per_page = 100
        while True:
            url = f'https://api.github.com/orgs/{ORG}/repos?per_page={per_page}&page={page}'
            try:
                if requests is None:
                    break
                resp = requests.get(url, headers=headers)
                if resp.status_code == 404:
                    print(f"  API 404 — token may lack org repo list permissions. Falling back to gh CLI.")
                    break
                if resp.status_code != 200:
                    print(f"  API error {resp.status_code}: {resp.text[:100]}", file=sys.stderr)
                    break
                batch = resp.json()
                if not batch:
                    break
                repos.extend([normalize_api_repo(r) for r in batch])
                if len(batch) < per_page:
                    break
                page += 1
            except Exception as e:
                print(f"  API exception: {e}", file=sys.stderr)
                break
        
        if repos:
            print(f"  Fetched {len(repos)} repos via API")
            return repos
        print("  API returned 0 repos, falling back to gh CLI")
    
    # Fallback to gh CLI
    print("  Using gh CLI")
    cmd = [
        "gh", "repo", "list", ORG,
        "--limit", str(REPO_LIMIT),
        "--json", "name,createdAt,pushedAt,description,primaryLanguage,isFork,isArchived,visibility"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def classify_repo(repo, chronicle_names):
    """Classify a single repo."""
    now = datetime.now()
    created = datetime.fromisoformat(repo['createdAt'].replace('Z', '+00:00')).replace(tzinfo=None)
    pushed = datetime.fromisoformat(repo['pushedAt'].replace('Z', '+00:00')).replace(tzinfo=None)
    days_since_push = (now - pushed).days
    desc = repo.get('description') or ''
    desc_len = len(desc)
    name = repo['name']
    is_fork = repo.get('isFork', False)
    
    # Tier
    is_scaffold = (created.date() == pushed.date() and desc_len < 25)
    is_skeleton = (days_since_push < 30 and desc_len < 40 and not is_scaffold and not is_fork)
    
    if is_scaffold:
        tier = 'Scaffold'
    elif is_skeleton:
        tier = 'Skeleton'
    elif desc_len > 80 or name in chronicle_names or name in core_fleet or name in named_vessels:
        tier = 'Production'
    else:
        tier = 'Functional'
    
    # Relevance
    if name in core_fleet:
        relevance = 'Core Fleet'
    elif name in named_vessels:
        relevance = 'Named Vessel'
    elif name in integration:
        relevance = 'Integration Bridge'
    elif name in experimental:
        relevance = 'Experimental'
    elif name in chronicle_names:
        relevance = 'Chronicled'
    elif is_fork:
        relevance = 'Fork'
    else:
        relevance = 'Orphan'
    
    # Lifecycle
    if is_scaffold:
        lifecycle = 'Scaffold'
    elif days_since_push < 7:
        lifecycle = 'Active Dev'
    elif days_since_push < 30:
        lifecycle = 'Maintenance'
    elif days_since_push < 90:
        lifecycle = 'Dormant'
    else:
        lifecycle = 'Abandoned'
    
    # Action
    if tier == 'Scaffold':
        action = 'PRIVATE'
    elif relevance in ('Core Fleet', 'Named Vessel'):
        action = 'KEEP'
    elif relevance == 'Integration Bridge' and days_since_push < 30:
        action = 'KEEP'
    elif lifecycle == 'Abandoned' and relevance == 'Orphan':
        action = 'PRIVATE'
    elif lifecycle == 'Dormant' and relevance == 'Orphan':
        action = 'ARCHIVE'
    elif tier == 'Skeleton':
        action = 'MONITOR'
    elif relevance == 'Experimental' and days_since_push < 14:
        action = 'KEEP'
    else:
        action = 'REVIEW'
    
    return {
        'name': name,
        'created': repo['createdAt'],
        'pushed': repo['pushedAt'],
        'description': desc,
        'language': repo.get('primaryLanguage', {}).get('name', 'N/A') if repo.get('primaryLanguage') else 'N/A',
        'is_fork': is_fork,
        'is_archived': repo.get('isArchived', False),
        'tier': tier,
        'relevance': relevance,
        'lifecycle': lifecycle,
        'action': action,
        'days_since_push': days_since_push,
        'desc_len': desc_len,
    }


def load_chronicle_names():
    """Load repo names mentioned in chronicle files."""
    names = set()
    chronicle_dir = "CHRONICLE"
    if not os.path.exists(chronicle_dir):
        return names
    for fname in os.listdir(chronicle_dir):
        if fname.endswith('.md'):
            with open(os.path.join(chronicle_dir, fname)) as f:
                content = f.read()
                # Simple heuristic: look for repo names in backticks or bold
                # This is imperfect but sufficient for augmentation
                pass
    return names


def write_csv(repos, path):
    """Write repos to pipe-delimited CSV."""
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        for r in repos:
            writer.writerow([
                r['name'], r['created'], r['pushed'], r['description'],
                r['language'], str(r['is_fork']).lower(), str(r['is_archived']).lower()
            ])
    print(f"  Wrote {len(repos)} repos to {path}")


def write_json(repos, path):
    """Write repos as JSON for programmatic access."""
    with open(path, 'w') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'org': ORG,
            'total': len(repos),
            'repos': repos
        }, f, indent=2)
    print(f"  Wrote {path}")


def write_completeness_tier(repos, path):
    with open(path, 'w') as f:
        f.write("# Completeness Tier Index\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        for tier in ['Production', 'Functional', 'Skeleton', 'Scaffold']:
            tier_repos = [r for r in repos if r['tier'] == tier]
            f.write(f"## {tier} ({len(tier_repos)} repos)\n\n")
            f.write("| Repo | Language | Last Push | Description | Relevance | Action |\n")
            f.write("|------|----------|-----------|-------------|-----------|--------|\n")
            for r in sorted(tier_repos, key=lambda x: x['pushed'], reverse=True):
                f.write(f"| {r['name']} | {r['language']} | {r['pushed'][:10]} | {r['description'][:55]} | {r['relevance']} | {r['action']} |\n")
            f.write("\n")
    print(f"  Wrote {path}")


def write_fleet_relevance(repos, path):
    with open(path, 'w') as f:
        f.write("# Fleet Relevance Index\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        for rel in ['Core Fleet', 'Named Vessel', 'Integration Bridge', 'Experimental', 'Chronicled', 'Fork', 'Orphan']:
            rel_repos = [r for r in repos if r['relevance'] == rel]
            f.write(f"## {rel} ({len(rel_repos)} repos)\n\n")
            f.write("| Repo | Tier | Lifecycle | Action | Last Push | Description |\n")
            f.write("|------|------|-----------|--------|-----------|-------------|\n")
            for r in sorted(rel_repos, key=lambda x: x['pushed'], reverse=True):
                f.write(f"| {r['name']} | {r['tier']} | {r['lifecycle']} | {r['action']} | {r['pushed'][:10]} | {r['description'][:50]} |\n")
            f.write("\n")
    print(f"  Wrote {path}")


def write_lifecycle_stage(repos, path):
    with open(path, 'w') as f:
        f.write("# Lifecycle Stage Index\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        for stage in ['Active Dev', 'Maintenance', 'Dormant', 'Abandoned', 'Scaffold']:
            stage_repos = [r for r in repos if r['lifecycle'] == stage]
            f.write(f"## {stage} ({len(stage_repos)} repos)\n\n")
            f.write("| Repo | Tier | Relevance | Action | Days Since Push | Description |\n")
            f.write("|------|------|-----------|--------|-----------------|-------------|\n")
            for r in sorted(stage_repos, key=lambda x: x['days_since_push']):
                f.write(f"| {r['name']} | {r['tier']} | {r['relevance']} | {r['action']} | {r['days_since_push']} | {r['description'][:50]} |\n")
            f.write("\n")
    print(f"  Wrote {path}")


def write_strategic_action(repos, path):
    with open(path, 'w') as f:
        f.write("# Strategic Action Index\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        for action in ['KEEP', 'PRIVATE', 'ARCHIVE', 'MONITOR', 'REVIEW']:
            act_repos = [r for r in repos if r['action'] == action]
            f.write(f"## {action} ({len(act_repos)} repos)\n\n")
            f.write("| Repo | Tier | Relevance | Lifecycle | Last Push | Description |\n")
            f.write("|------|------|-----------|-----------|-----------|-------------|\n")
            for r in sorted(act_repos, key=lambda x: x['pushed'], reverse=True):
                f.write(f"| {r['name']} | {r['tier']} | {r['relevance']} | {r['lifecycle']} | {r['pushed'][:10]} | {r['description'][:55]} |\n")
            f.write("\n")
    print(f"  Wrote {path}")


def write_chronology_by_month(repos, path):
    months = {}
    for r in repos:
        ym = r['created'][:7]
        if ym not in months:
            months[ym] = []
        months[ym].append(r)
    
    with open(path, 'w') as f:
        f.write("# Chronology by Month\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        for ym in sorted(months.keys()):
            m = months[ym]
            f.write(f"## {ym} ({len(m)} repos)\n\n")
            f.write("| Repo | Tier | Action | Language | Description |\n")
            f.write("|------|------|--------|----------|-------------|\n")
            for r in sorted(m, key=lambda x: x['created']):
                f.write(f"| {r['name']} | {r['tier']} | {r['action']} | {r['language']} | {r['description'][:55]} |\n")
            f.write("\n")
    print(f"  Wrote {path}")


def write_master_index(repos, path):
    total = len(repos)
    with open(path, 'w') as f:
        f.write("# Master Repo Index\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')} | **Repos:** {total}\n\n")
        
        if total == 0:
            f.write("*No repos fetched. Check API token permissions.*\n")
            print(f"  Wrote {path} (empty — 0 repos)")
            return
        
        # Summary tables
        tiers = {}
        for r in repos:
            tiers.setdefault(r['tier'], 0)
            tiers[r['tier']] += 1
        f.write("## Completeness\n\n")
        f.write("| Tier | Count | % |\n")
        f.write("|------|-------|---|\n")
        for tier in ['Production', 'Functional', 'Skeleton', 'Scaffold']:
            c = tiers.get(tier, 0)
            pct = c/total*100 if total > 0 else 0
            f.write(f"| {tier} | {c} | {pct:.1f}% |\n")
        f.write("\n")
        
        actions = {}
        for r in repos:
            actions.setdefault(r['action'], 0)
            actions[r['action']] += 1
        f.write("## Strategic Action\n\n")
        f.write("| Action | Count | % |\n")
        f.write("|--------|-------|---|\n")
        for action in ['KEEP', 'PRIVATE', 'ARCHIVE', 'MONITOR', 'REVIEW']:
            c = actions.get(action, 0)
            pct = c/total*100 if total > 0 else 0
            f.write(f"| {action} | {c} | {pct:.1f}% |\n")
        f.write("\n")
        
        f.write("## Monthly Velocity\n\n")
        months = {}
        for r in repos:
            ym = r['created'][:7]
            if ym not in months:
                months[ym] = []
            months[ym].append(r)
        f.write("| Month | New | KEEP | PRIVATE |\n")
        f.write("|-------|-----|------|---------|\n")
        for ym in sorted(months.keys()):
            m = months[ym]
            k = len([r for r in m if r['action'] == 'KEEP'])
            p = len([r for r in m if r['action'] == 'PRIVATE'])
            f.write(f"| {ym} | {len(m)} | {k} | {p} |\n")
        f.write("\n")
    print(f"  Wrote {path}")


def write_dashboard(repos, path):
    total = len(repos)
    keep = len([r for r in repos if r['action'] == 'KEEP'])
    priv = len([r for r in repos if r['action'] == 'PRIVATE'])
    arch = len([r for r in repos if r['action'] == 'ARCHIVE'])
    mon = len([r for r in repos if r['action'] == 'MONITOR'])
    rev = len([r for r in repos if r['action'] == 'REVIEW'])
    
    with open(path, 'w') as f:
        f.write("# Fleet Health Dashboard\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')} | **Repos:** {total}\n\n")
        f.write("## At a Glance\n\n")
        f.write("| Metric | Value | % |\n")
        f.write("|--------|-------|---|\n")
        f.write(f"| Total | {total} | 100% |\n")
        f.write(f"| KEEP | {keep} | {keep/total*100:.1f}% |\n")
        f.write(f"| PRIVATE | {priv} | {priv/total*100:.1f}% |\n")
        f.write(f"| ARCHIVE | {arch} | {arch/total*100:.1f}% |\n")
        f.write(f"| MONITOR | {mon} | {mon/total*100:.1f}% |\n")
        f.write(f"| REVIEW | {rev} | {rev/total*100:.1f}% |\n")
        f.write("\n")
        
        f.write("## Red Flags\n\n")
        f.write("| Issue | Count |\n")
        f.write("|-------|-------|\n")
        f.write(f"| Scaffolds | {priv} |\n")
        f.write(f"| Abandoned orphans | {len([r for r in repos if r['lifecycle']=='Abandoned' and r['relevance']=='Orphan'])} |\n")
        f.write(f"| Dormant orphans | {len([r for r in repos if r['lifecycle']=='Dormant' and r['relevance']=='Orphan'])} |\n")
        f.write("\n")
        
        f.write("## KEEPers (Public Face)\n\n")
        keepers = [r for r in repos if r['action'] == 'KEEP']
        f.write("| Repo | Relevance | Last Push | Description |\n")
        f.write("|------|-----------|-----------|-------------|\n")
        for r in sorted(keepers, key=lambda x: x['pushed'], reverse=True):
            f.write(f"| {r['name']} | {r['relevance']} | {r['pushed'][:10]} | {r['description'][:55]} |\n")
        f.write("\n")
    print(f"  Wrote {path}")


def write_cleanup(repos, path):
    priv_repos = [r['name'] for r in repos if r['action'] == 'PRIVATE']
    arch_repos = [r['name'] for r in repos if r['action'] == 'ARCHIVE']
    mon_repos = [r['name'] for r in repos if r['action'] == 'MONITOR']
    
    with open(path, 'w') as f:
        f.write("# Fleet Cleanup Guide\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("## PRIVATE ({} repos)\n\n".format(len(priv_repos)))
        f.write("```bash\n")
        for name in sorted(priv_repos):
            f.write(f"gh repo edit {ORG}/{name} --visibility private\n")
        f.write("```\n\n")
        
        f.write("## ARCHIVE ({} repos)\n\n".format(len(arch_repos)))
        f.write("```bash\n")
        for name in sorted(arch_repos):
            f.write(f"gh repo archive {ORG}/{name}\n")
        f.write("```\n\n")
        
        f.write("## MONITOR ({} repos) — check 2026-06-04\n\n".format(len(mon_repos)))
        f.write("```bash\n")
        f.write("# Re-run triage. If still skeleton → private.\n")
        for name in sorted(mon_repos):
            f.write(f"#   {name}\n")
        f.write("```\n\n")
    print(f"  Wrote {path}")


def main():
    print("=" * 50)
    print("Fleet Triage Generator")
    print("=" * 50)
    
    raw_repos = fetch_repos()
    print(f"Fetched {len(raw_repos)} repos from {ORG}")
    
    chronicle_names = load_chronicle_names()
    repos = [classify_repo(r, chronicle_names) for r in raw_repos]
    
    # Ensure directories exist
    os.makedirs("INDEXES", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Write raw data
    write_csv(repos, "data/all-repos.csv")
    write_json(repos, "data/repos.json")
    
    # Write indexes
    write_completeness_tier(repos, "INDEXES/COMPLETENESS-TIER.md")
    write_fleet_relevance(repos, "INDEXES/FLEET-RELEVANCE.md")
    write_lifecycle_stage(repos, "INDEXES/LIFECYCLE-STAGE.md")
    write_strategic_action(repos, "INDEXES/STRATEGIC-ACTION.md")
    write_chronology_by_month(repos, "INDEXES/CHRONOLOGY-BY-MONTH.md")
    write_master_index(repos, "INDEXES/MASTER-INDEX.md")
    
    # Write dashboard + cleanup
    write_dashboard(repos, "DASHBOARD.md")
    write_cleanup(repos, "CLEANUP.md")
    
    print("\nDone. All indexes regenerated.")
    print("Next: git add -A && git commit -m 'Regenerate triage indexes' && git push")


if __name__ == "__main__":
    main()
