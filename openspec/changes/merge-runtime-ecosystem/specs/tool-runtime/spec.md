## ADDED Requirements
### Requirement: Plan tool detection
The system SHALL treat registered skills as plan tools and expose them via the tool runtime.

#### Scenario: Skill marked as plan tool
- **WHEN** a skill is registered with the skill registry
- **THEN** the tool runtime reports is_plan_tool as true for that skill name

### Requirement: WorkUnit tool loop
The system SHALL enforce Envelope budgets and DonePredicate completion when executing WorkUnit tools.

#### Scenario: DonePredicate satisfied
- **WHEN** the tool loop produces evidence that satisfies the DonePredicate
- **THEN** the tool runtime returns a successful ToolResult
