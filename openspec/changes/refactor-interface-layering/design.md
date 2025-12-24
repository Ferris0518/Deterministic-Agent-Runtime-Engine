## Context
Design documents define a two-layer interface split: Layer 1 (core infrastructure) and Layer 2 (pluggable components). Currently interfaces are grouped in a single module, which conflicts with the intended structure.

## Goals / Non-Goals
- Goals:
  - Separate Layer 1 and Layer 2 interfaces into distinct modules.
  - Align naming, imports, and exports with the layer definitions.
- Non-Goals:
  - Changing interface behavior or signatures beyond relocation.
  - Rewriting component implementations.

## Decisions
- Decision: Create `dare_framework/core/interfaces.py` for Layer 1 interfaces.
- Decision: Keep Layer 2 interfaces under `dare_framework/components/interfaces.py` (or `dare_framework/components/layer2.py`) and re-export as needed.
- Decision: Add compatibility re-exports to avoid breaking existing imports during migration.

## Risks / Trade-offs
- Risk: Import changes may ripple through examples/tests.
  - Mitigation: Provide re-exports and update internal imports in one change.

## Migration Plan
- Introduce new interface modules and update imports across core/runtime/components.
- Add re-exports in `dare_framework/interfaces.py` or `dare_framework/components/__init__.py` to keep compatibility.

## Open Questions
- Which public import paths should be preserved for backward compatibility?
