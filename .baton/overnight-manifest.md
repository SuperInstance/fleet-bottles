# Overnight Fleet Manifest — 2026-05-21
# Autonomous operation while user sleeps. Check results in the morning.

## Background Processes (Running Now)

| Process | PID | Status | Output | Expected Completion |
|---------|-----|--------|--------|---------------------|
| overnight_distillation.py | 364427 | RUNNING (46% CPU) | /tmp/overnight_distillation.log, .json | ~6-8 hours (200 epochs) |
| overnight_tournament.py | 364722 | RUNNING (37% CPU) | /tmp/overnight_tournament.log, .json | ~30 seconds (1000 gens) |

## Subagent Queue (Spawn as slots free)

### Wave 3 — Validation & Fixes (5 agents, ~5-15m each)
| Agent | Mission | Status |
|-------|---------|--------|
| jepa-benchmark | Prove 2.35ms/10K claim | RUNNING |
| distillation-1epoch | Measure epoch time, extrapolate | RUNNING |
| tournament-dynamic-cap | Fix Lighthouse Effect with dynamic cap | RUNNING |
| hardware-adaptive-threshold | Fix XDNA2 starvation per-device | RUNNING |
| zero-coverage-tests | Write tests for pathos, distill, swarm | RUNNING |

### Wave 4 — Deep Experiments (spawn after Wave 3)
| Agent | Mission | Builds On | Novel Question |
|-------|---------|-----------|---------------|
| tournament-long-sim | 5000 generations, multiple cap strategies | Wave 2/3 tournament results | Does dynamic cap prevent premature convergence at scale? |
| hardware-extended-sim | 10K timesteps, 6 load profiles | Wave 2/3 hardware results | At what load does adaptive thresholding break down? |
| grammar-engine-fix | Fix input validation from CCC audit | MEMORY.md Grammar Engine finding | Can we sanitize the chaos rules without breaking legitimate evolution? |
| nexus-localhost-fix | Fix Federated Nexus hardcoded localhost | MEMORY.md Nexus bug | Will fixing the IP restore fleet-wide registration? |
| cross-repo-duplication | Deep clone 20 repos, find duplication | Wave 2 cross-repo patterns | Which capabilities are re-implemented >10 times? |
| plato-breeding-curriculum | Design agent onboarding for Plato rooms | SPEC-BREEDER.md | Can a bred agent reach "able-bodied crewman" in <50 moves? |

### Wave 5 — Morning Synthesis (spawn before user wakes)
| Agent | Mission | Input |
|-------|---------|-------|
| overnight-report | Compile all results into morning brief | All Wave 3/4 outputs + background process logs |
| github-issue-triage | File issues for bugs found | Test gap results, grammar audit, nexus fix |
| next-wave-planner | Design Wave 6 based on overnight findings | All novel insights from Waves 1-5 |

## Checkpoints
- Every hour, write status to /tmp/overnight_fleet_status.txt
- Every 2 hours, check background processes: ps aux | grep overnight_
- When tournament sim finishes, restart with different parameters (cap=100, no dynamic cap)
- When distillation hits epoch 100, push checkpoint to GitHub LFS or copy to workspace

## Morning Deliverables (for user)
1. Overnight results summary (accuracies, fitness curves, benchmark numbers)
2. All PRs merged or ready for review
3. New questions raised by overnight experiments
4. Wave 6 plan — what to run next
