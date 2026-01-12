## ADDED Requirements
### Requirement: Workspace roots in configuration
The system SHALL expose `workspace_roots: list[str]` in the effective configuration so tools can enforce write scope, defaulting to the project root for local development.

#### Scenario: Default workspace roots
- **WHEN** no explicit workspace roots are configured
- **THEN** the effective configuration includes the current project root as the sole workspace root

### Requirement: Local command execution tool
The system SHALL provide a `RunCommandTool` that executes shell commands with the working directory restricted to a configured workspace root.

#### Scenario: Command runs in an allowed workspace
- **WHEN** the tool is invoked with a working directory under `workspace_roots`
- **THEN** the command executes and the tool returns stdout, stderr, and exit status

#### Scenario: Command rejected outside workspace roots
- **WHEN** the tool is invoked with a working directory outside `workspace_roots`
- **THEN** the tool returns a failure result indicating the directory is not allowed
