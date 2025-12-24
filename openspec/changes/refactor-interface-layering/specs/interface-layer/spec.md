## MODIFIED Requirements
### Requirement: Layered interface separation
The system SHALL organize interface definitions according to architectural layers, separating Layer 1 (core infrastructure) interfaces from Layer 2 (pluggable component) interfaces.

#### Scenario: Layer 1 interface location
- **WHEN** a developer looks for core infrastructure interfaces (e.g., IRuntime, IEventLog, IToolRuntime, IPolicyEngine, IPlanGenerator, IValidator, IRemediator, IContextAssembler)
- **THEN** the interfaces are defined in a dedicated Layer 1 module under `dare_framework/core/`

#### Scenario: Layer 2 interface location
- **WHEN** a developer looks for pluggable component interfaces (e.g., IModelAdapter, IMemory, ITool, ISkill, IToolkit, IMCPClient, IHook, ICheckpoint)
- **THEN** the interfaces are defined in a dedicated Layer 2 module under `dare_framework/components/`

## ADDED Requirements
### Requirement: Compatibility re-exports
The system SHALL provide compatibility re-exports for existing public interface import paths during the migration.

#### Scenario: Legacy import path
- **WHEN** a consumer imports interfaces using the legacy module path
- **THEN** the import resolves without error and refers to the Layer 1 or Layer 2 definition
