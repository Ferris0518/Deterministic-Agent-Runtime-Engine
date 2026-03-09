---
change_ids: ["transport-typed-payload-cutover"]
doc_kind: feature
topics: ["transport", "typed-payload", "agent-runtime", "client", "protocol"]
created: 2026-03-09
updated: 2026-03-09
status: archived
mode: openspec
---

# Feature: transport-typed-payload-cutover

## Scope
移除 transport 运行时剩余的 legacy 兼容层：删除 `TransportEnvelope.event_type` 与 `message/action/control` 的 raw payload 兼容，把 request/reply 全面收敛到 typed payload families。

## OpenSpec Artifacts
- Proposal: `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/proposal.md`
- Design: `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/design.md`
- Specs:
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/specs/typed-transport-replies/spec.md`
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/specs/transport-channel/spec.md`
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/specs/interaction-dispatch/spec.md`
  - `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/specs/chat-runtime/spec.md`
- Tasks: `openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/tasks.md`

## Progress
- 已完成：transport/runtime/client/example transport typed payload cutover。
- 已完成：OpenSpec tasks 1.1-4.2 与对应回归验证。

## Evidence

### Commands
- `openspec new change "transport-typed-payload-cutover"`
- `openspec status --change "transport-typed-payload-cutover" --json`
- `openspec instructions proposal --change "transport-typed-payload-cutover" --json`
- `openspec instructions design --change "transport-typed-payload-cutover" --json`
- `openspec instructions specs --change "transport-typed-payload-cutover" --json`
- `openspec instructions tasks --change "transport-typed-payload-cutover" --json`
- `./.venv/bin/pytest -q tests/unit/test_transport_types.py tests/unit/test_transport_channel.py tests/unit/test_transport_adapters.py tests/unit/test_interaction_dispatcher.py tests/unit/test_base_agent_transport_contract.py tests/unit/test_agent_event_transport_hook.py tests/unit/test_react_agent_gateway_injection.py tests/unit/test_example_10_agentscope_compat.py`
- `./.venv/bin/pytest -q tests/unit/test_examples_cli.py tests/unit/test_examples_cli_mcp.py tests/unit/test_dare_agent_hook_transport_boundary.py tests/unit/test_client_cli.py -k 'approvals or transport or approval_pending or hook or event'`
- `./.venv/bin/pytest -q tests/unit/test_transport_types.py tests/unit/test_transport_channel.py tests/unit/test_transport_adapters.py tests/unit/test_interaction_dispatcher.py tests/unit/test_base_agent_transport_contract.py tests/unit/test_agent_event_transport_hook.py tests/unit/test_react_agent_gateway_injection.py tests/unit/test_example_10_agentscope_compat.py tests/unit/test_examples_cli.py tests/unit/test_examples_cli_mcp.py tests/unit/test_client_cli.py tests/unit/test_dare_agent_hook_transport_boundary.py tests/integration/test_client_cli_flow.py`
- `git diff --check`
- `openspec validate --changes "transport-typed-payload-cutover"`

### Results
- transport request/reply 已全面收敛到 typed payload families。
- `pytest` focused transport/runtime/example/client suite: `178 passed, 1 warning`
- `git diff --check`: passed
- `openspec validate --changes "transport-typed-payload-cutover"`: `14 passed, 0 failed`

### Contract Delta
- `schema`: changed
  - 移除 `event_type`
  - 移除 raw string/dict transport payload
  - request/reply 均收敛到 typed payload families
- `error semantics`: changed
  - message/action/control 的错误回复改由对应 typed payload 自身字段表达
- `retry`: none
  - 本切片不调整 retry/timeout 策略

### Golden Cases
- 更新：typed transport/unit/example/client regression fixtures
- 新增：`openspec/changes/archive/2026-03-09-transport-typed-payload-cutover/**`

### Regression Summary
- transport/runtime/example/client targeted regression suite passed with typed request/reply contract.

### Observability and Failure Localization
- `start`: typed payload request enters `TransportEnvelope(kind, payload)`
- `tool_call`: ReactAgent emits `MessagePayload(message_kind=tool_call/tool_result)`
- `end`: BaseAgent/default channel reply with `MessagePayload/ActionPayload/ControlPayload`
- `fail`: invalid typed payload family now fails at envelope construction or deterministic payload validation branch

### Structured Review Report
- module boundary:
  - transport reply 语义回收到 payload family，不再分叉到 `event_type`
- state:
  - 不涉及 session/resume/cache
- concurrency:
  - 主要风险在 request/reply 契约切换造成 client/test 同步修改
- side-effect:
  - 会破坏 legacy transport consumers，属于明确 breaking change
- coverage:
  - transport/runtime/example/client/unit+integration 回归已覆盖

### Behavior Verification
- Happy path:
  - `message` request -> `MessagePayload(chat)` reply
  - `action` request -> `ActionPayload(ok/result)` reply
  - approval pending -> `SelectPayload(ask, approval)`
- Error branch:
  - invalid payload family rejected deterministically
  - action failure returns `ActionPayload(ok=False, code, reason)`
  - agent execution failure returns `MessagePayload(summary, data.reason/code)`

### Risks and Rollback
- 风险：大量 tests/examples 依赖 `event_type + dict payload`
- 回滚：整体回退到当前 transport 兼容契约

### Review and Merge Gate Links
- Intent PR: 待补
- Review request: 待补
- Merge gate: 待补
