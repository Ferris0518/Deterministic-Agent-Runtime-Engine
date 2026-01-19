## 1. Configuration model
- [x] 1.1 Define layered config schema (system, project, user, session overrides) covering model/MCP/tool/validator/hook sections and allow/deny lists.
- [x] 1.2 Implement ConfigProvider merging + validation against schema and expose namespaced access to effective config.

## 2. Session wiring
- [x] 2.1 Attach effective config to SessionContext during session init and persist a snapshot for event log/debug.
- [x] 2.2 Add minimal tests covering merge precedence and SessionContext exposure.

## 3. Component loading from config
- [x] 3.1 Allow validators/tools/hooks (and composite tools) to be enabled/disabled or composed from config entries alongside entry point discovery.
- [x] 3.2 Cover config-driven component selection with unit tests.
