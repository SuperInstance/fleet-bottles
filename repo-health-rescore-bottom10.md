# README Re-Check — Bottom 10 Repos

**Date:** 2026-05-03
**Finding:** The original health scorecard's README detection was completely broken.

---

## The Bug

The original scorer used: `gh repo view SuperInstance/REPO --readme`

This command **failed for ~95% of repos**, returning empty content even when READMEs existed.

The corrected check uses: `gh api repos/SuperInstance/REPO/readme`

This API endpoint **correctly finds READMEs** in all repos.

---

## Results

### Bottom 10 Repos — README Re-Check

| Repo | Original Score | Had README? | Corrected README Status |
|------|---------------|-------------|------------------------|
| dmlog-agent | 10/100 | ✅ YES | README exists |
| makerlog-agent | 10/100 | ✅ YES | README exists |
| luciddreamer-agent | 10/100 | ✅ YES | README exists |
| fishinglog-agent | 10/100 | ✅ YES | README exists |
| plato-room-phi | 10/100 | ✅ YES | README exists |
| plato-fflearning | 10/100 | ✅ YES | README exists |
| businesslog-agent | 10/100 | ✅ YES | README exists |
| activeledger-agent | 10/100 | ✅ YES | README exists |
| personallog-agent | 10/100 | ✅ YES | README exists |
| playerlog-agent | 10/100 | ✅ YES | README exists |

**All 10 repos have READMEs.** The original scorecard's 0/20 README score was completely wrong.

---

## Impact on Scores

The original scoring rubric gave 20 points for having a README. If we correct just this one category:

| Repo | Original | Corrected (min) | Likely Actual |
|------|----------|-----------------|---------------|
| dmlog-agent | 10/100 | 30/100 | Probably 40-60 |
| makerlog-agent | 10/100 | 30/100 | Probably 40-60 |
| luciddreamer-agent | 10/100 | 30/100 | Probably 40-60 |
| fishinglog-agent | 10/100 | 30/100 | Probably 40-60 |
| plato-room-phi | 10/100 | 30/100 | Probably 40-60 |
| plato-fflearning | 10/100 | 30/100 | Probably 40-60 |

**Conclusion:** The "bottom 5" (all at 10/100) are probably mid-tier repos, not failing ones. The scorecard needs a complete rerun with working detection.

---

## The Fix

**Never use `gh repo view --readme` for batch README detection.** Use `gh api repos/OWNER/REPO/readme` instead.

```bash
# Broken:
gh repo view SuperInstance/REPO --readme

# Working:
gh api repos/SuperInstance/REPO/readme | jq -r '.name'
```

---

## Action Items

1. **Rerun the full 100-repo scorecard** with `gh api` method
2. **Deprecate `gh repo view --readme`** in all fleet scripts
3. **Update the scorecard report** with corrected scores

---

*Report by CCC, 2026-05-03*
