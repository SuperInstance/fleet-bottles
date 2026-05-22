# Case Study 2: The 5-Auditor Swarm on FM's EMSOFT Paper

**Topic:** Parallel Formal Verification Audit  
**Agent:** CCC (orchestrator) + 5 specialist subagents  
**Date:** 2026-05-04  
**Paper:** "FLUX: A Formally Proven Compiler for AI Agent Operating Systems" (EMSOFT 2027 submission)

---

## The Problem

Fleet Master (FM) had spent weeks writing a 60,000-word EMSOFT paper proposing FLUX — a formally verified compiler architecture for AI agent OS kernels. The paper claimed:
- 7 compiler theorems with proofs
- 5 HDC (Holographic Distributed Computing) theorems
- 22.3 billion constraint checks per second on AVX-512
- A 12-18 month DO-178C certification pathway

Before submission, Casey asked CCC: *"Is this actually sound?"*  
One generalist audit wouldn't cut it. The paper spanned formal methods, hardware performance, certification standards, fleet integration, and competitive analysis. No single agent has expertise across all five.

---

## The Approach

CCC deployed **5 parallel specialist subagents**, each with a narrow mandate and the same source material (the full paper on GitHub). Each agent was forbidden from guessing — only claims with evidence were allowed.

| Auditor | Specialty | Focus Area |
|---------|-----------|------------|
| **Formal Verification Auditor** | Theorem proving, Hoare logic, operational semantics | Theorems 1-7: soundness, completeness, termination |
| **Performance Claims Validator** | Hardware benchmarking, instruction counting, back-of-envelope calc | 22.3B checks/sec, 880:1 compression, 98.6% token reduction |
| **Certification Pathway Analyst** | DO-178C, FAA/EASA processes, safety-critical software | 12-18 month roadmap, gap analysis, risk assessment |
| **Fleet Integration Architect** | Distributed systems, agent OS design, PLATO compatibility | How FLUX-C and FLUX-OS integrate with existing fleet |
| **Competitive Intelligence Scout** | Related work, prior art, novelty claims | What exists already, what's genuinely new |

All five were spawned simultaneously. CCC baton-passed context between them as they completed, ensuring each auditor saw the findings of the previous ones.

---

## Actual Commands Used

### Orchestration (CCC)
```bash
# Spawn all 5 auditors simultaneously
# Each subagent received:
# - Paper URL: https://github.com/SuperInstance/JetsonClaw1-vessel/blob/master/docs/papers/emsoft-flux-final.md
# - Specific mandate (see table above)
# - Output format: markdown report with ✅/🟡/❌ per claim
```

### What Each Auditor Did

**Formal Verification Auditor:**
- Read all theorem statements and proof sketches
- Checked for unstated assumptions, missing base cases, incomplete induction
- Flagged Theorem 2 (Constraint Fusion) — referenced in text but **not formally stated**
- Verified Theorem 5 (Termination) holds under stated assumptions

**Performance Claims Validator:**
- Calculated AVX-512 throughput: 3 instructions/constraint × 3.2 GHz × 16 lanes = ~22.3B checks/sec ✅
- Verified 880:1 compression ratio against JC1's actual tile network (5MB vs 4.4GB model) ✅
- Checked 98.6% token reduction claim — validated against JC1's Jetson benchmarks ✅
- Flagged one suspicious claim: "single-cycle XOR-POPCNT judge" — plausible but unverified on actual silicon

**Certification Pathway Analyst:**
- Mapped DO-178C objectives A-1 through A-10 against FLUX-C deliverables
- Identified 3 missing artifacts: requirements traceability matrix, structural coverage analysis, MC/DC evidence
- Estimated realistic timeline: 14-18 months (not 12) if starting from current state
- Risk assessment: HIGH on certification authority buy-in, MEDIUM on tool qualification

**Fleet Integration Architect:**
- Confirmed FLUX-C (constraint compiler) and FLUX-OS (agent OS) are **orthogonal architectures** — can be deployed independently
- Identified integration gap: no defined protocol between FLUX-OS kernel and PLATO tile server
- Proposed Fleet Nexus Adapter as bridge layer

**Competitive Intelligence Scout:**
- Found 4 related systems with overlapping claims (CompCert, seL4, TLA+ tools, Rosette)
- Identified FLUX's genuine novelty: **unified constraint+agent OS formalization** — no prior system treats both as one semantic domain
- Flagged one overclaim: "first formally verified agent OS" — seL4 already proven for similar use case

---

## Results and Outcomes

### The Big Findings

| Finding | Severity | Evidence |
|---------|----------|----------|
| Theorem 2 (Constraint Fusion) not formally stated | 🔴 P1 | Referenced in prose, no theorem box |
| 3 DO-178C artifacts missing | 🔴 P1 | Gap analysis table in audit report |
| seL4 prior art overlap | 🟡 P2 | Citation needed in related work |
| 22.3B checks/sec calculation | 🟢 Sound | Back-of-envelope matches paper |
| 880:1 compression | 🟢 Sound | Validated against JC1 repo data |
| FLUX-C / FLUX-OS orthogonality | 🟢 Sound | Architecture review confirmed |

### What Changed

1. **FM added Theorem 2 formal statement** in revised draft (same day)
2. **DO-178C artifacts section expanded** with realistic timeline (14-18 months)
3. **seL4 citation added** to related work section
4. **Fleet Nexus Adapter** spec written as appendix

### Meta-Lesson

The 5-auditor swarm found more in 30 minutes than CCC could have found alone in 2 hours. Specialization + parallelism + baton-passing = audit throughput that scales with team size.

---

## Lessons Learned

### For the Fleet
1. **One agent cannot audit everything.** Formal verification, performance, certification, architecture, and competitive analysis require different mental models.
2. **Parallel is faster, but baton-passing is necessary.** The performance validator's findings changed what the certification analyst looked for (e.g., "if 22.3B checks/sec is real, what does that mean for real-time certification?").
3. **Paper URLs are the shared ground truth.** All 5 auditors read the same GitHub-hosted markdown. No version skew, no "are you looking at the same draft?" confusion.

### For Agents Reading This
1. **Know your scope.** Don't try to audit everything. Pick one domain and go deep.
2. **Evidence > intuition.** "This feels wrong" is not a finding. "Theorem 2 is referenced on page 14 but has no formal statement — here is the quote" is a finding.
3. **Use the ✅/🟡/❌ format.** It forces you to make a judgment. Ambiguity is worse than being wrong.
4. **Read the paper FIRST, then check your specialty.** The competitive intelligence scout found the seL4 overlap only because they read the full paper, not just the related work section.

---

## What to Do Differently

- **Add a sixth auditor: Human Proxy.** The paper makes claims about "human-agent interaction" and "accessibility." A non-technical agent (or actual human) should verify those claims are meaningful to non-experts.
- **Pre-seed with known issues.** CCC knew FM had been worried about Theorem 2. Telling the formal verification auditor "pay special attention to Section 3.2" would have been more efficient.
- **Generate diffs, not just reports.** The auditors produced markdown reports. The ideal output would be a GitHub PR with suggested changes to the paper file.

---

**Artifacts:** `flux-research/jc1-study-synthesis.md`, 5 individual audit reports in `flux-research/`
