## MODIFIED Requirements
### Requirement: Tool manager contract
The tool domain SHALL define an `IToolManager` contract in `dare_framework/tool/kernel.py` that extends `IToolGateway`. The contract SHALL support trusted tool registration, provider aggregation, and prompt tool definition export without executing tools. At minimum it MUST include:
- `register_tool(...)`, `unregister_tool(...)`, `update_tool(...)`
- `register_provider(...)`, `unregister_provider(...)`
- awaitable `list_capabilities(...)`, `refresh(...)`
- `list_tool_defs(...)`, `get_capability(...)`
- `health_check(...)`

Implementations MAY expose a synchronous capability snapshot helper for synchronous runtime assembly paths, but this helper MUST return the same trusted `CapabilityDescriptor` model as `list_capabilities(...)`.

#### Scenario: Awaitable capability listing is stable for gateway callers
- **GIVEN** the default `ToolManager` implementation is used as `IToolGateway`
- **WHEN** callers execute `await list_capabilities()`
- **THEN** the result is `list[CapabilityDescriptor]`
- **AND** no sync/async type mismatch error is raised by awaiting callers

### Requirement: Trusted tool listings for model prompts
Context and runtime model-input assembly SHALL source tool availability from the trusted capability registry exposed by `IToolGateway.list_capabilities()`; tool listings MUST NOT originate from untrusted sources (planner/model output).

`ModelInput.tools` MUST carry `CapabilityDescriptor` entries. Model adapters are responsible for converting these trusted descriptors into provider-specific tool-definition payloads.

#### Scenario: Context assembles capability descriptors for model adapters
- **GIVEN** context is wired with the default `ToolManager`
- **WHEN** context assembles tool listings for a model request
- **THEN** each item is a `CapabilityDescriptor`
- **AND** adapters can access descriptor fields (`name`, `description`, `input_schema`) without dict coercion
