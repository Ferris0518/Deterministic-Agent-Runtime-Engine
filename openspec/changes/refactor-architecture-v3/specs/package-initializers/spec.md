## MODIFIED Requirements
### Requirement: Contracts are defined in dedicated modules
The framework SHALL define contract surfaces (protocols, enums, dataclasses, and domain exceptions) in dedicated modules (e.g., `protocols.py`, `models.py`, `errors.py`) and SHALL NOT define them in `__init__.py`.

#### Scenario: Finding a protocol definition
- **WHEN** a contributor needs to inspect `IExecutionControl`
- **THEN** the protocol is defined in a dedicated module, not in `__init__.py`.

#### Scenario: Finding a model definition
- **WHEN** a contributor needs to inspect `RunLoopState`
- **THEN** the enum is defined in a dedicated module, not in `__init__.py`.

### Requirement: Package initializers are minimal except facades
All package initializers under `dare_framework3/**/__init__.py` SHALL contain only documentation and metadata constants, except for designated facade packages which MAY re-export stable API symbols.

#### Scenario: Auditing internal package initializers
- **WHEN** auditing `dare_framework3/_internal/**/__init__.py`
- **THEN** the file contains only an optional docstring and metadata constants and contains no import statements.

#### Scenario: Auditing a facade package initializer
- **WHEN** auditing `dare_framework3/interfaces/__init__.py`
- **THEN** it re-exports stable interface symbols and contains no class or function definitions.

### Requirement: No pass-through re-export modules
The framework SHALL avoid modules whose sole purpose is re-exporting symbols, except for designated facade packages.

#### Scenario: Removing a non-facade re-export
- **WHEN** a module contains only re-export imports and `__all__`
- **THEN** it is removed unless it is a designated facade package.
