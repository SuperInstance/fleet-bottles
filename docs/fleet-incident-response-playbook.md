# Fleet Incident Response Playbook

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**Status:** Living document — update as fleet evolves

---

## Philosophy

**A Captain doesn't just restart things. They understand why it broke, whether restarting is safe, and how to prevent it happening again.**

---

## Incident Severity Levels

| Level | Name | Response Time | Example |
|-------|------|---------------|---------|
| P0 | Fleet-critical | Immediate | PLATO down, MUD unreachable, security breach |
| P1 | Service-critical | 30 min | Grammar Engine down, Nexus broken, cocapn.ai 404 |
| P2 | Degraded | 2 hours | Dashboard stale, ZC feed lagging, broken exits |
| P3 | Cosmetic | 24 hours | Copy errors, outdated stats, missing alt text |

---

## P0 Response: Fleet-Critical Incident

### Step 1: Detect (0-2 min)

Run the health check:
```bash
python3 scripts/fleet-health-check.py
```

Confirm the failure is real (not a network glitch):
```bash
# Check from multiple angles
curl -s http://147.224.38.131:8847/status
curl -s http://147.224.38.131:4042/status
ping -c 3 147.224.38.131
```

If all fail → **Host-level issue**. Check Oracle1's machine.
If one fails → **Service-level issue**. Proceed to diagnosis.

### Step 2: Notify (2-5 min)

**Immediate:**
- Drop a bottle to `data/bottles/fleet/` with "P0" in title
- If security-related, drop to `data/bottles/direct/` for Casey

**Bottle template:**
```markdown
[I2I:BOTTLE] CCC 🦀 → Fleet — P0: [SERVICE] DOWN

## Impact
- Service: [name]
- Endpoint: [URL]
- Error: [what you see]
- Since: [timestamp]
- Affected: [what breaks because of this]

## Diagnosis
[What you've checked so far]

## Action Taken
[What you've done]

## Next Steps
- [ ] Task 1
- [ ] Task 2
```

### Step 3: Diagnose (5-15 min)

**Service crash:**
```bash
# If you have SSH access to Oracle1
ssh oracle1-vessel
sudo systemctl status [service]
sudo journalctl -u [service] -n 50 --no-pager
```

**No SSH access (most agents):**
- Check PLATO tiles for recent changes to the service
- Check git commits in the relevant repo
- Check if the service port responds at all (connection refused vs timeout vs HTTP error)

### Step 4: Act (15-30 min)

**If you have control:**
```bash
# Restart service
sudo systemctl restart [service]

# Or if it's a Python script
pkill -f [script_name]
cd /path/to/service && python3 [script_name].py &
```

**If you don't have control (most cases):**
- Document the exact failure mode
- Propose a fix in a bottle
- If Casey is online, escalate directly
- If not, leave a detailed bottle and monitor

### Step 5: Verify (30-35 min)

```bash
python3 scripts/fleet-health-check.py
# Confirm the service is UP
```

### Step 6: Log (35-45 min)

Update the incident in `data/bottles/fleet/`:
```markdown
## Resolution
- Fixed at: [timestamp]
- Fix: [what was done]
- Verification: [health check output]

## Prevention
- [ ] Add monitoring for this failure mode
- [ ] Add auto-restart
- [ ] Document the fix
```

---

## Common Incident Patterns

### Pattern: Port 4047 (Federated Nexus) Connection Refused

**Symptom:** `curl: (7) Failed to connect to 147.224.38.131 port 4047: Connection refused`

**Diagnosis:**
```bash
# Check if anything listens on 4047
nmap -p 4047 147.224.38.131
```

**Likely cause:** Service not running or crashed.

**Fix (if you have access):**
```bash
# Known issue: hardcoded localhost instead of IP
cd /path/to/nexus
# Edit federation.py line 203: replace localhost with 147.224.38.131
python3 nexus/federation.py &
```

**Fix (if you don't have access):** Drop bottle to Oracle1 with the exact line to change.

### Pattern: Grammar Engine SyntaxError

**Symptom:** `SyntaxError at grammar/core.py:147`

**Likely cause:** Chaos rule ingestion — un-sanitized input reached the parser.

**Diagnosis:**
```bash
# Check evolution log for injected payloads
curl -s http://147.224.38.131:4045/status  # If it responds at all
```

**Fix:**
1. Stop the grammar engine
2. Clear the poisoned rules from the evolution log
3. Add input sanitization to rule creation endpoint
4. Restart

**Prevention:**
- Sanitize rule names (alphanumeric + underscore only)
- Validate field types (no `<script>` in taglines)
- Sandboxed execution for `production.exec`

### Pattern: cocapn.ai 404 Pages

**Symptom:** `/plato`, `/fleet`, `/papers`, `/flux` return 404

**Diagnosis:** These pages were planned but never built.

**Fix options:**
1. Build them (PHP pages)
2. Remove references from nav/copy
3. Add redirects to working pages

### Pattern: PLATO Tile Rejection

**Symptom:** `POST /submit` returns `{"accepted": false, "reason": "..."}`

**Common causes:**
- Missing required field (domain, question, answer)
- Invalid confidence value (must be 0.0-1.0)
- Domain doesn't exist (create it first)

**Fix:** Check the response message and resubmit with corrections.

---

## Monitoring Setup

### What to Monitor

| Check | Frequency | Method | Alert Threshold |
|-------|-----------|--------|-----------------|
| MUD status | Every 5 min | `curl .../4042/status` | HTTP != 200 |
| PLATO status | Every 5 min | `curl .../8847/status` | HTTP != 200 |
| Grammar Engine | Every 5 min | `curl .../4045/status` | HTTP != 200 |
| Arena | Every 5 min | `curl .../4044/status` | HTTP != 200 |
| Fleet Dashboard | Every 10 min | `curl .../4046/` | Connection refused |
| cocapn.ai | Every 10 min | `curl https://cocapn.ai/` | HTTP >= 500 |
| GitHub repos | Every hour | GitHub API | New commits (info only) |

### Automated Health Check

```bash
# Add to crontab (on a machine that can reach Oracle1)
*/5 * * * * cd /path/to/fleet-bottles && python3 scripts/fleet-health-check.py --json > /tmp/fleet-health.json 2>&1
```

### Alerting

For now, alerts are manual:
1. Run health check
2. If any service is DOWN, write a bottle
3. If P0, also notify Casey

**Future:** Wire health check to Feishu/Discord webhook for automatic alerts.

---

## Escalation Ladder

| Severity | First Responder | Escalation Path |
|----------|-----------------|-----------------|
| P0 | Any agent who detects it | Casey (direct bottle) + Fleet (broadcast) |
| P1 | Agent assigned to service | Oracle1 (bottle) + FM (if code-related) |
| P2 | Agent who owns the area | Relevant agent bottle + Fleet log |
| P3 | CCC (design/copy) | No escalation — fix when convenient |

---

## Recovery Checklist

After any P0/P1 incident, verify:

- [ ] Service responds to health checks
- [ ] No data loss (check logs, tiles, commits)
- [ ] Dependent services unaffected
- [ ] Incident logged in `data/bottles/fleet/`
- [ ] Root cause understood
- [ ] Prevention measure identified
- [ ] No secrets exposed in logs

---

## Tools Reference

| Tool | Purpose | Location |
|------|---------|----------|
| `fleet-health-check.py` | Check all endpoints | `scripts/fleet-health-check.py` |
| `fleet-repo-monitor.py` | Track repo commits | `scripts/fleet-repo-monitor.py` |
| `fleet-status-report.py` | Generate reports | `scripts/fleet-status-report.py` |
| `lesson-to-tile.py` | Curriculum → PLATO | `scripts/lesson-to-tile.py` |

---

## Contact Reference

| Person | Role | Bottle Path |
|--------|------|-------------|
| Casey | Captain | `data/bottles/direct/` |
| Oracle1 🔮 | Lighthouse | `data/bottles/oracle1/` |
| Forgemaster ⚒️ | Builder | `data/bottles/forgemaster/` |
| JetsonClaw1 ⚡ | Edge | `data/bottles/jetsonclaw1/` |
| CCC 🦀 | Design/Research | `data/bottles/fleet/` |

---

*This playbook is a living document. Update it after each incident.*

— CCC 🦀
*Fleet I&O Officer*
*2026-05-05*
