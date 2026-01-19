## 1. Implementation
- [x] 1.1 Inventory `dare_framework/**/__init__.py` patterns (definitions, re-exports, import glue).
- [x] 1.2 For each affected Kernel domain, create `models.py` / `protocols.py` / `errors.py` as needed and move
      contract definitions out of `__init__.py`.
- [x] 1.3 Convert all `dare_framework/**/__init__.py` files to metadata-only:
      allow metadata constants (e.g., `__version__`); forbid `class` / `def`, imports, and re-exports.
- [x] 1.4 Remove pass-through re-export modules (e.g., `components/*/protocols.py` that only re-export contracts)
      and update imports to module-of-definition paths.
- [x] 1.5 Update all internal imports across `dare_framework/`, `examples/`, and `tests/` to use module-of-definition
      paths (compatibility is explicitly out of scope).
- [x] 1.6 Add a unit test that asserts:
      - no `dare_framework/**/__init__.py` contains top-level `class`/`def` definitions
      - `__init__.py` contains no import statements
- [x] 1.7 Run `ruff`, `black --check`, `mypy --strict`, and `pytest`; fix any failures introduced by the refactor.
      - Note: `ruff`/`black`/`mypy` may be unavailable in this environment; `pytest` should run and pass.

## 2. Validation Evidence
- [x] 2.1 Capture the initializer-structure check output in the PR/notes.
      - `pytest -q` includes `test_package_initializers_metadata_only`
- [x] 2.2 Capture test results (`pytest`) in the PR/notes.
      - `pytest -q` → `22 passed`
