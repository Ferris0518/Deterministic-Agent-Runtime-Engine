# Change: Refactor framework architecture to v3 (new package)

## Why
The current codebase contains two parallel frameworks (v1 and v2) with overlapping concepts and divergent layouts. The v3 architecture in `doc/ARCHITECTURE_COMPARISON.md` clarifies kernel boundaries, fixes domain ownership (context/memory, security), and introduces a stable public API facade. Aligning implementations with that architecture reduces fragmentation and creates a clear migration path while introducing `dare_framework3` as a new package.

## What Changes
- Introduce `dare_framework3/` with the v3 model (public API facades + `_internal` domain packages).
- Move memory and prompt store into the context domain.
- Create a dedicated security domain with `ISecurityBoundary` as the kernel interface and security components as pluggable interfaces.
- Split domain interfaces into `kernel.py` and `components.py` to distinguish Layer 0 vs Layer 2.
- Add context engineering components (`IRetriever`, `IIndexer`) and security components (`ITrustVerifier`, `IPolicyEngine`, `ISandbox`).
- Introduce a presets system in the public API surface.
- Refactor `dare_framework/` and `dare_framework2/` to align with the v3 domain layout, ownership rules, and kernel/components split.
- Update builder wiring, imports, examples, and docs to match the new structures.
- **BREAKING**: internal module paths and some import locations will change.

## Impact
- Affected specs: `kernel-layout`, `organize-layered-structure`, `define-core-interfaces`, `define-core-models`, `interface-layer`, `define-trust-boundary`, `package-facades`, `package-initializers`.
- Affected code: `dare_framework/`, `dare_framework2/`, new `dare_framework3/`, and relevant docs/tests/examples.
