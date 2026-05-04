# Competitive Intelligence: seL4 and WASM-Embedded
**CCC, Fleet R&D Officer | 2026-05-05**
**For:** EMSOFT 2027 Paper — Table 3 "Related Work Comparison"

---

## seL4 — The Formally Verified Microkernel

| Attribute | Detail |
|-----------|--------|
| **What** | Microkernel with machine-checked formal proof of functional correctness |
| **Size** | 8,700 lines of C + 600 lines of assembly |
| **Proof** | Isabelle/HOL — abstract spec → C implementation → binary translation |
| **Guarantees** | No buffer overflows, null pointers, use-after-free, or unsafe operations |
| **Performance** | 224 cycles one-way IPC (ARM) — comparable to unverified L4 kernels |
| **Platforms** | ARM (v6/v7/v8, 22 platforms verified), x86, RISC-V |
| **Certification** | Strong evidence for DO-254 — formal proof reduces certification overhead |
| **Limitations** | Assumes compiler/hardware correctness; multicore proof incomplete; no VM layer |
| **Latest** | 2025 — 100% of ARM platforms verified; integrity proof on AArch64 complete |

**Why FLUX is different:**
- seL4 is a *microkernel* — no VM, no constraint language, no DSL for safety properties
- FLUX provides a *constraint DSL* (GUARD) + *verified VM* + *formal compiler* in one stack
- seL4 proves the kernel is correct; FLUX proves the *application's safety constraints* are correct
- seL4 requires OS expertise; FLUX targets embedded developers who aren't OS engineers

**Citation:** Klein et al. "seL4: Formal Verification of an OS Kernel." SOSP 2009.

---

## Wasmtime / WAMR — The Sandboxed Runtime

| Attribute | Detail |
|-----------|--------|
| **What** | WebAssembly runtime for server-side and embedded execution |
| **Safety** | Memory sandboxed, type-safe, control-flow integrity by design |
| **Performance** | Low overhead, AOT compilation, fast startup |
| **Portability** | ISA-independent bytecode, runs on any host |
| **Formal Verification** | ❌ None. Multiple CVEs 2024-2026 prove this |
| **CVEs** | Heap buffer overflow (CVE-2024-34251), memory corruption (CVE-2025-64713), DoS (CVE-2026-27572), path traversal (CVE-2024-51745) |
| **Real-Time** | ❌ No guarantees. GC and JIT introduce unpredictability |
| **Certification** | ❌ Not suitable for DO-254 DAL A |
| **Resource Isolation** | Weak — WASI interfaces expose attack surface; resource exhaustion attacks possible |

**Why FLUX is different:**
- WASM is *sandboxed* but not *verified* — memory safety ≠ functional correctness
- FLUX provides *formal verification* of constraint satisfaction
- WASM has no constraint DSL — you write Rust/C and hope it's safe
- FLUX has deterministic execution (no GC, no JIT, no hidden costs)
- WASM CVEs show runtime bugs are real; FLUX's proof eliminates this class of errors

**Citation:** "Wasmtime." Bytecode Alliance, 2024. https://wasmtime.dev/

---

## Competitive Positioning Map

```
                    High Verification
                          ↑
                          |
    seL4 (kernel)    ←———+———→    FLUX (VM + constraints)
    [proven correct]        |        [proven constraints]
                          |
    ——————————————————————+——————————————————————
    Low DSL               |               High DSL
    Support               |               Support
                          |
    Traditional C       ←———+———→    WASM-Embedded
    [no safety]           |        [sandboxed, unverified]
                          |
                          ↓
                    Low Verification
```

**FLUX's unique quadrant:** High verification + High DSL support.
- seL4 has high verification but no DSL (you write C on top of it)
- WASM has a DSL (WASM itself) but no verification
- Traditional C has neither
- FLUX has both: a constraint DSL that compiles to verified bytecode

---

## Suggested Table 3 Rows for EMSOFT Paper

| System | Verification | Constraint DSL | Real-Time | Size | Certification Path |
|--------|------------|----------------|-----------|------|------------------|
| seL4 | ✅ Full (Isabelle/HOL) | ❌ None | ✅ Yes | ~9K LOC | DO-254 (strong evidence) |
| Wasmtime | ❌ None (CVEs exist) | ❌ None | ❌ No | ~100K+ LOC | ❌ Not suitable |
| FLUX-C | ✅ Two-pass compiler proof | ✅ GUARD | ✅ WCET analyzable | ~2KB VM | DO-254 DAL A (planned) |
| FLUX-X | 🟡 JIT (Cranelift/LLVM) | ✅ GUARD | 🟡 JIT-dependent | ~2KB+ VM | 🟡 TBD |

**Footnote for table:** "seL4 verification assumes compiler, assembly, and hardware correctness. FLUX verification includes compiler correctness proof (semantic equivalence). Wasmtime has no formal verification; multiple CVEs (2024-2026) demonstrate runtime vulnerabilities."

---

## Key Talking Points for Paper

1. **"seL4 proves the kernel is correct. FLUX proves your safety constraints are correct."**
   - Different layers of the stack. Complementary, not competing.

2. **"WASM is sandboxed, not verified. Sandboxing catches accidents; verification eliminates bugs."**
   - The CVE list proves sandboxing isn't enough for safety-critical systems.

3. **"FLUX is the only system with both a constraint DSL and a formal verification path."**
   - This is the unique value proposition. No other system occupies this quadrant.

4. **"FLUX's VM is smaller than seL4's kernel (2KB vs 9K LOC)."**
   - Size matters for certification — less code to verify, less surface area.

---

## Risks to Acknowledge

1. **FLUX is younger than seL4.** seL4 has 15+ years of deployment. FLUX is new.
   - Counter: FLUX builds on established techniques (refinement, stack machines, linear typing)

2. **seL4's proof is more comprehensive.** It covers the entire kernel.
   - Counter: FLUX's proof covers the constraint-to-bytecode pipeline, which is the novel contribution

3. **WASM has broader ecosystem.** More tools, more languages, more developers.
   - Counter: FLUX targets safety-critical embedded, not general-purpose computing

---

*"The question isn't whether FLUX is better than seL4. The question is whether FLUX is better than C on seL4 for expressing safety constraints. The answer is yes."*
*— CCC, 2026-05-05*
