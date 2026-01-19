## ADDED Requirements

### Requirement: Contracts are defined in dedicated modules
The framework SHALL define contract surfaces (protocols, enums, dataclasses, and domain exceptions) in
dedicated modules (e.g., `protocols.py`, `models.py`, `errors.py`) and SHALL NOT define them in `__init__.py`.

#### Scenario: Finding a protocol definition
- **WHEN** a contributor needs to inspect `IExecutionControl`
- **THEN** the protocol is defined in a dedicated module (e.g.,
  `dare_framework/core/execution_control/protocols.py`)
- **AND** it is not defined in `dare_framework/core/execution_control/__init__.py`

#### Scenario: Finding a model definition
- **WHEN** a contributor needs to inspect `RunLoopState`
- **THEN** the enum is defined in a dedicated module (e.g., `dare_framework/core/run_loop/models.py`)
- **AND** it is not defined in `dare_framework/core/run_loop/__init__.py`

### Requirement: Package initializers are metadata-only (no re-exports)
All package initializers under `dare_framework/**/__init__.py` SHALL contain only documentation (docstring
and optional comments) plus metadata constants (e.g., `__version__`). They SHALL NOT import/re-export
symbols from other modules, and SHALL NOT contain top-level `class` / `def` statements.

#### Scenario: Auditing package initializers
- **WHEN** auditing `dare_framework/**/__init__.py`
- **THEN** the file contains only an optional docstring and metadata constants
- **AND** it contains no `class` / `def` statements
- **AND** it contains no import statements

### Requirement: No pass-through re-export modules
The framework SHALL avoid modules whose sole purpose is re-exporting symbols from another module (for example,
re-exporting a shared contract from `contracts/` under a different path).

#### Scenario: Removing a pass-through re-export
- **WHEN** a contributor finds a module that contains only re-export imports and `__all__`
- **THEN** it is removed and call sites import from the module-of-definition instead
