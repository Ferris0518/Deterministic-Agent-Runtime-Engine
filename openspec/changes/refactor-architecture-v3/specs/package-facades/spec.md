## MODIFIED Requirements
### Requirement: Package facades
Designated facade packages (`dare_framework3`, `dare_framework3.interfaces`, `dare_framework3.types`, `dare_framework3.presets`, `dare_framework3.builder`) SHALL re-export the symbols intended for public use via `from .module import Class` and `__all__ = [...]`. Other packages SHALL NOT be treated as facades.

#### Scenario: Facade subpackage exports public members
- **GIVEN** a facade package directory with submodules
- **WHEN** the package is imported
- **THEN** its `__init__.py` re-exports the classes and objects intended for public use.

### Requirement: No direct definitions in initializers
`__init__.py` files SHALL NOT contain class or function definitions.

#### Scenario: Definitions stay in submodules
- **GIVEN** a need for a new class in a package
- **WHEN** the developer implements it
- **THEN** it is defined in a separate submodule (like `models.py` or `protocols.py`), not in `__init__.py`.

### Requirement: Documentation in initializers
Every `__init__.py` file SHALL have a docstring or comments describing the package's purpose.

#### Scenario: Package has a docstring
- **GIVEN** an `__init__.py` file
- **THEN** it starts with a docstring or includes comments explaining what the package contains and its responsibility.
