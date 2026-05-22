# FORKS — Upstream Sources

**Total forks in SuperInstance:** 10  
**Total original repos:** 190 (of 200 sampled)  
**Fork rate:** 5%

---

## Fork Registry

| Repo | Upstream | Language | Purpose | Integration Status |
|------|----------|----------|---------|-------------------|
| automerge | automerge/automerge | JavaScript | JSON-like CRDT | Active research |
| DeepGEMM | deepseek-ai/DeepGEMM | CUDA | FP8 GEMM kernels | FM→JC1 pipeline |
| MemEye | upstream/MemEye | Python | Visual memory eval | Oracle1 integrated |
| openarm | upstream/openarm | MDX | Humanoid robot arm | Physical AI research |
| openhuman | upstream/openhuman | Rust | Personal AI | Consumer integration |
| OpenShell | upstream/OpenShell | Rust | Safe agent runtime | Fleet OS target |
| pbft-rust | upstream/pbft-rust | Rust | PBFT consensus | Research comparison |
| terax-ai | upstream/terax-ai | TypeScript | AI terminal emulator | 7MB runtime |
| tri-quarter-toolbox | upstream/tri-quarter-toolbox | Python | Math framework | Math foundation |
| zeroclaw | Lucineer/zeroclaw | TypeScript | Agent framework | Ancestor of all ZC |

---

## The Lucineer Connection

**zeroclaw** is forked from `Lucineer/zeroclaw`. This is significant because:

1. **Lucineer** is also a SuperInstance repo (created 2026-03-13, "Project for Lucineer, likely a search engine tool")
2. The Lucineer project appears to be a **precursor identity** or **collaborator**
3. ZeroClaw was developed under the Lucineer name before being adopted into the fleet
4. The fleet's "repo-native agent" philosophy may have originated in the Lucineer project

**Hypothesis:** The creator operated as "Lucineer" before adopting "SuperInstance" / "Cocapn Fleet" as the primary identity. The Lucineer → SuperInstance transition represents a shift from individual project work to fleet-scale agent orchestration.

---

## Fork Strategy

The fleet uses forks for **three purposes**:

### 1. Research Integration (DeepGEMM, MemEye)
Fork upstream projects, add fleet-specific bridges and documentation, contribute back if possible.

### 2. Runtime Integration (OpenShell, terax-ai)
Fork projects that become part of the fleet infrastructure. Wrap them, extend them, make them fleet-native.

### 3. Historical Ancestry (zeroclaw)
Fork from precursor projects that contain the DNA of fleet concepts. Maintain the lineage.

---

## Non-Fork Policy

95% of SuperInstance repos are **original work**. The fleet prefers:
- Writing new implementations over forking
- Creating custom dialects (constraint-theory-mlir)
- Building from first principles (eisenstein, pythagorean48)
- Reimplementing concepts in 15+ languages rather than wrapping one upstream

The 5% fork rate reflects **strategic integration** of high-value upstream projects, not dependency.

---

## Upstream Health

| Fork | Upstream Activity | Fleet Divergence |
|------|-------------------|-----------------|
| automerge | Very active (CRDT standard) | Minimal — research use |
| DeepGEMM | Active (DeepSeek project) | Fleet-specific optimizations |
| MemEye | Active (multimodal eval) | Oracle1 ecosystem integration |
| openarm | Active (robotics project) | Physical AI research |
| openhuman | Active (personal AI) | Consumer integration |
| OpenShell | Active (safe runtime) | Fleet OS compatibility layer |
| pbft-rust | Stable (reference impl) | Research comparison only |
| terax-ai | Active (terminal emulator) | API gateway integration |
| tri-quarter-toolbox | Active (math framework) | Fleet math foundation |
| zeroclaw | Archived (Lucineer) | Superseded by fleet-native agents |

---

*"5% borrowed, 95% built. The fleet builds before it borrows."*
