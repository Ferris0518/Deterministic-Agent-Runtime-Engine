---
change_ids: ["message-input-boundary-cleanup"]
doc_kind: feature
topics: ["message-schema", "agent-input", "transport", "session-loop", "examples"]
created: 2026-03-09
updated: 2026-03-09
status: archived
mode: openspec
---

# Feature: message-input-boundary-cleanup

## Scope
收口 canonical message 的剩余输入边界问题：agent 顶层直接接受 `Message`，`Task` 退回编排对象并通过 `input_message` 保存真实用户消息，transport poll loop 不再把 `MessagePayload` 压扁成字符串。

本特性仍然只覆盖 message 本身相关改动，不包含消息投递/缓存/压缩/resume/分发设计。

## OpenSpec Artifacts
- Proposal: `openspec/changes/message-input-boundary-cleanup/proposal.md`
- Design: `openspec/changes/message-input-boundary-cleanup/design.md`
- Specs:
  - `openspec/changes/message-input-boundary-cleanup/specs/rich-media-message-schema/spec.md`
  - `openspec/changes/message-input-boundary-cleanup/specs/transport-channel/spec.md`
  - `openspec/changes/message-input-boundary-cleanup/specs/session-loop/spec.md`
  - `openspec/changes/message-input-boundary-cleanup/specs/plan-module/spec.md`
- Tasks: `openspec/changes/message-input-boundary-cleanup/tasks.md`

## Evidence

### Commands
- `./.venv/bin/pytest -q tests/unit/test_base_agent_transport_contract.py -k canonical_message_payload`
- `./.venv/bin/pytest -q tests/unit/test_session_orchestrator_message_input.py tests/unit/test_context_message_types.py -k 'input_message or requires_structured_data_for_tool'`
- `./.venv/bin/pytest -q tests/unit/test_base_agent_transport_contract.py tests/unit/test_session_orchestrator_message_input.py tests/unit/test_context_message_types.py tests/unit/test_examples_04_cli.py tests/unit/test_examples_cli.py tests/unit/test_examples_cli_mcp.py tests/unit/test_client_cli.py tests/unit/test_dare_agent_hook_governance.py tests/unit/test_react_agent_gateway_injection.py tests/unit/test_five_layer_agent.py`
- `./.venv/bin/pytest -q tests/unit/test_transport_typed_payloads.py tests/unit/test_transport_types.py tests/unit/test_transport_channel.py tests/unit/test_transport_adapters.py tests/unit/test_openai_model_adapter.py tests/unit/test_openrouter_adapter.py tests/unit/test_anthropic_model_adapter.py tests/unit/test_context_implementation.py tests/unit/test_context_compression.py tests/unit/test_checkpoint_message_schema.py`
- `./.venv/bin/pytest -q tests/unit/test_client_cli.py tests/integration/test_client_cli_flow.py -k 'conversation_id or mode_plan or execute or run_task'`
- `./.venv/bin/pytest -q tests/unit/test_dare_agent_hook_governance.py tests/unit/test_react_agent_gateway_injection.py tests/unit/test_five_layer_agent.py`

### Results
- transport loop now passes canonical `Message` into agent execution without dropping attachments.
- session loop now prefers `Task.input_message` over `Task.description`.
- canonical schema now rejects `tool_call/tool_result` messages without `data`.
- active client/example direct prompt entry points now send `Message`.

### Contract Delta
- `schema`: changed
  - `IAgent.__call__` accepts `str | Message`; internal execute/orchestration paths consume canonical `Message`.
  - `Task` adds `input_message`.
- `error semantics`: changed
  - `tool_call/tool_result` without `data` now fail at canonical message construction.
- `retry`: none
  - no runtime retry semantics changed.

### Regression Summary
- focused unit and example suites passed.
- client CLI focused integration slice passed.

### Risks and Rollback
- remaining docs/spec references to `str | Task` outside the touched scope still need broader cleanup.
- rollback would require reverting the public `str | Message` boundary normalization and the `Task.input_message` internal projection.
