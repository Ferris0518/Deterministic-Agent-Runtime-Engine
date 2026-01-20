## Context
The repository currently contains two framework variants (`dare_framework` and `dare_framework2`) with different layouts. The v3 proposal in `doc/ARCHITECTURE_COMPARISON.md` specifies domain ownership fixes (context/memory, security) and a mixed architecture with explicit kernel/components separation per domain and a stable public API facade. The v3 package will be introduced as a new `dare_framework3/` package.

## Goals / Non-Goals
- Goals:
  - Introduce `dare_framework3/` aligned to the v3 architecture proposal.
  - Clarify kernel vs component boundaries via `kernel.py` and `components.py` per domain.
  - Provide a stable public API facade and internal implementation boundary.
  - Add missing context engineering and security component interfaces.
  - Refactor `dare_framework/` and `dare_framework2/` to the v3 domain layout and ownership rules.
- Non-Goals:
  - Redesign runtime behavior beyond required interface moves.
  - Introduce new execution semantics unrelated to the architecture layout.

## Decisions
- Decision: Adopt a public facade + `_internal` domain layout for `dare_framework3/`.
  - Rationale: Matches the v3 proposal and provides clear stability boundaries.
- Decision: Move memory and prompt store into context components across v2/v3.
  - Rationale: Aligns with Context Engineering ownership.
- Decision: Split security into its own domain with kernel interface and pluggable components across v2/v3.
  - Rationale: Security is a kernel-level concern shared across domains.
- Decision: Add `IRetriever`, `IIndexer`, `ITrustVerifier`, `IPolicyEngine`, `ISandbox` interfaces as component contracts.
  - Rationale: Completes context and security sub-systems in v3.

## Risks / Trade-offs
- Large refactor risk: broad import and wiring changes may cause regressions.
- Spec conflicts: `package-facades` and `package-initializers` currently conflict and must be reconciled.
- Compatibility: internal path changes will break consumers that import non-facade modules.

## Migration Plan
1. Update specs and finalize layout decisions.
2. Refactor v2 code to v3 layout (least fragmented base).
3. Refactor v1 code to match v3 ownership rules and layout conventions.
4. Scaffold `dare_framework3` with facade and internal packages.
5. Add compatibility notes or shims for legacy imports.

## Open Questions
- (Resolved) `dare_framework3` is introduced as a new package alongside v1/v2.
- (Resolved) Facade-style re-exports are allowed only for designated facade packages.
