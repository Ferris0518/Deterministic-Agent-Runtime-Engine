## ADDED Requirements
### Requirement: Model Partitioning
Core data models SHALL be grouped into domain modules under `dare_framework/core/models/` (config, runtime, plan, tool, event, context, memory, MCP, results).

#### Scenario: Locating a data model
- **WHEN** a contributor needs `ToolDefinition`
- **THEN** it is located in the tooling domain module under `dare_framework/core/models/`.

### Requirement: Plan Model Staging
The framework SHALL keep proposed and validated plan step models distinct, without aliasing proposal models as validated models.

#### Scenario: Distinguishing plan stages
- **WHEN** a contributor reads the plan models
- **THEN** proposed steps and validated steps are represented by separate types with explicit names.
