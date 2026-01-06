# Change: Refactor layered structure and clarify interfaces/models

## Why
The current layout concentrates many interfaces and data models in single files and includes multiple pass-through modules that only re-export symbols. This makes the three-layer architecture harder to see, slows onboarding, and obscures the intended responsibilities described in the design docs. It also diverges from common Python library organization patterns (clear domain modules, explicit public API, minimal re-export glue), which makes the codebase feel less idiomatic and harder to navigate for Python developers.

## What Changes
- Reorganize modules to align with the three-layer model and functional domains, following Pythonic package structuring patterns seen in mature libraries (explicit subpackages, curated API surface).
- Split core interfaces and models into domain-focused modules with explicit naming.
- Remove re-export-only modules and keep package `__init__.py` files minimal (no implementation re-exports).
- Add concise design-intent comments on interfaces and abstract methods per the design docs.
- Introduce an explicit `ITrustBoundary` interface to model the design-doc trust boundary step and its data derivation responsibilities.
- Update examples/tests/imports to match the new layout.

## Impact
- Affected specs: organize-layered-structure, define-core-interfaces, define-core-models, define-trust-boundary
- Affected code: dare_framework/*, examples/*, tests/*
