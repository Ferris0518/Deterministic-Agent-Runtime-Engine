## 1. Inventory and Design
- [x] 1.1 Audit all `__init__.py` files and identify public members for each package level.
- [x] 1.2 Define the "facade" pattern and ensure it doesn't re-introduce the coupling problems previously solved (e.g. by avoiding circular imports).

## 2. Implementation
- [x] 2.1 Update `dare_framework/core` subpackages to export public protocols and models.
- [x] 2.2 Update `dare_framework/components` subpackages to export public component classes.
- [x] 2.3 Update `dare_framework/contracts` and other top-level packages.
- [x] 2.4 Add `__all__` to all modified `__init__.py` files.

## 3. Verification
- [x] 3.1 Update `tests/unit/test_package_initializers_metadata_only.py` to `test_package_initializers_facade_pattern` asserting:
    - Docstrings are present.
    - No class definitions in `__init__.py`.
    - Imports are present but only for re-exporting.
- [x] 3.2 Run `pytest` to ensure no regressions or circular import issues.
