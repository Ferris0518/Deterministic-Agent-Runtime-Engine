## 1. Contract alignment
- [x] 1.1 Make `IToolGateway.list_capabilities()` awaitable in the interface contract.
- [x] 1.2 Update `ToolManager` to implement awaitable `list_capabilities()` and keep a sync capability snapshot helper for sync call sites.

## 2. Context/model-input type safety
- [x] 2.1 Ensure `Context.list_tools()` returns trusted `CapabilityDescriptor` entries (not tool-definition dicts).
- [x] 2.2 Preserve compatibility for legacy synchronous gateways.

## 3. Regression coverage and validation
- [x] 3.1 Add a regression test proving context tool assembly returns `CapabilityDescriptor` from `ToolManager`.
- [x] 3.2 Run targeted pytest for tool/context contract paths.
- [x] 3.3 Run `openspec validate fix-tool-capability-listing-contract --strict`.
