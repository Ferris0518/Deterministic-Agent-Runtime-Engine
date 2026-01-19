# Proposal: Refactor package exports to use __init__.py facades

## Why
The previous "metadata-only" refactor removed all imports from `__init__.py` files to satisfy a strict decoupling rule. However, this makes the library harder to use as developers must import from deep submodules (e.g., `from dare_framework.components.hooks.protocols import IHook` instead of `from dare_framework.components.hooks import IHook`). 

The user has requested a "facade" pattern where `__init__.py` files:
1. Contain descriptive docstrings.
2. Re-export public members (classes/objects) that the package is intended to expose.
3. Do NOT define classes directly in `__init__.py`.

This balances ease of use with the goal of keeping `__init__.py` files clean of implementation details.

## What Changes
- Update all `__init__.py` files in `dare_framework` to include proper docstrings.
- Add imports and `__all__` lists to `__init__.py` files to re-export public members from their respective submodules.
- Ensure no classes/logic are defined directly in `__init__.py`.
- Update or remove the `test_package_initializers_metadata_only` test as it's now obsolete.

## Impact
- **Developer Experience**: Improved. Easier imports for core and component members.
- **Breaking Changes**: None for existing code (this actually makes some imports more convenient, but existing deep imports will still work).
- **Architecture**: Transitions from "metadata-only" to "facade" initializers.
