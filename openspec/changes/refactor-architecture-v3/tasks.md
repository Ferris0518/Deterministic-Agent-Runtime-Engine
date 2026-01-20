## 1. Spec and design alignment
- [x] 1.1 Update OpenSpec deltas for v3 package layout, interfaces, and security/context ownership.
- [x] 1.2 Finalize v3 design decisions (facades vs internal packages, migration strategy, compatibility scope).

## 2. Refactor v1 and v2 frameworks
- [x] 2.1 Refactor `dare_framework2/` to the v3 domain layout (context/memory merge, security domain split, kernel/components split).
- [x] 2.2 Refactor `dare_framework/` to align with v3 layout and ownership rules (domain layout, kernel/components separation, security/context fixes).
- [x] 2.3 Update builder/composition wiring and imports to use the new interface locations.

## 3. Create dare_framework3 scaffold
- [x] 3.1 Scaffold `dare_framework3/` with public API facades, stable interfaces/types, presets, and `_internal` domain packages.
- [x] 3.2 Add placeholder implementations/stubs for new components (IRetriever, IIndexer, ITrustVerifier, IPolicyEngine, ISandbox).
- [x] 3.3 Add migration notes or compatibility shims for legacy imports.

## 4. Validation and docs
- [x] 4.1 Update architecture docs to reflect v3 structure and migration path.
- [x] 4.2 Run targeted tests or linting if requested (not requested).
