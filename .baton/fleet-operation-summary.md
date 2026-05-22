## Open PRs — 2026-05-21 Fleet Operation

| PR | Repo | Task | Status |
|----|------|------|--------|
| #1 | sunset-ecosystem | FLUX compat layer | ✅ Ready |
| #2 | sunset-ecosystem | JEPA Rust wire | ✅ Ready |
| #3 | sunset-ecosystem | Distillation experiment | ✅ Ready |
| #4 | sunset-ecosystem | Tournament sim | ✅ Ready |
| #5 | sunset-ecosystem | Hardware swarm sim | ✅ Ready |
| #6 | sunset-ecosystem | Test gap analysis | ✅ Ready |
| #1 | superinstance-wiki | Cross-repo patterns | ✅ Ready |
| #2 | superinstance-wiki | Repo metrics automation | ✅ Ready |

## Insights Captured
1. **Lighthouse Effect** — Perfect agent emerges at gen 16, population converges in its wake
2. **Graveyard of Dead Languages** — 8 flux-* repos in COBOL/ALGOL/SNOBOL/etc, all same day, all abandoned
3. **Fastest Device Does Least Work** — XDNA2 migration-starved by global thermal threshold
4. **3 Modules Zero Coverage** — pathos, distill, swarm have no tests
5. **Fleet Health: 75% Silver Tier** — 1,255 of 1,664 repos are mid-tier; only 3.3% Platinum

## Repo Metrics Formula
```
score = (relevance × 0.35 + completeness × 0.35 + lifecycle × 0.30) × 100 + strategic_bonus
```

## Timeout Lessons
- 10m: Too short for compilation, training, API pagination
- 15m: Good for code design + smoke tests
- 6m: Good for micro-simulations and lightweight analysis
- Zero-clone / zero-API: Eliminates biggest timeout risks
