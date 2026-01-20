## MODIFIED Requirements
### Requirement: Model Partitioning
Core data models SHALL be exposed from the stable type facade (`dare_framework3/types/`) and organized internally by domain under `dare_framework3/_internal/<domain>/types.py` (execution, context, security, tool, plan, model, protocols).

#### Scenario: Locating a data model
- **WHEN** a contributor needs `ToolDefinition`
- **THEN** it is available from `dare_framework3.types` and defined under `dare_framework3/_internal/tool/types.py`.

### Requirement: Plan Model Staging
The framework SHALL keep proposed and validated plan step models distinct, without aliasing proposal models as validated models.

#### Scenario: Distinguishing plan stages
- **WHEN** a contributor reads the plan models
- **THEN** proposed steps and validated steps are represented by separate types with explicit names in `dare_framework3/_internal/plan/types.py`.
