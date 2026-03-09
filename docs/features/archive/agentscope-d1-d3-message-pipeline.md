---
change_ids: ["agentscope-d1-d3-message-pipeline"]
doc_kind: feature
topics: ["agentscope", "message-schema", "transport", "context", "model", "rich-media"]
todo_ids: ["D1-1", "D1-2", "D1-3", "D1-4", "D2-1", "D2-2", "D2-3", "D2-4", "D3-1", "D3-2", "D3-3", "D3-4"]
created: 2026-03-09
updated: 2026-03-09
status: archived
mode: openspec
---

# Feature: agentscope-d1-d3-message-pipeline

## Scope
冻结消息格式基线，统一 transport typed payload、context canonical `Message` 与 model adapter codec 边界，首版支持单条 `chat` 消息携带“一段文字 + 多张图片”。

本特性只覆盖消息格式契约，不覆盖消息投递/缓存/压缩/resume/分发运行时设计。

## OpenSpec Artifacts
- Proposal: `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/proposal.md`
- Design: `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/design.md`
- Specs:
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/specs/rich-media-message-schema/spec.md`
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/specs/transport-channel/spec.md`
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/specs/chat-runtime/spec.md`
  - `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/specs/interaction-dispatch/spec.md`
- Tasks: `openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/tasks.md`

## Progress
- 已完成：design docs 基线更新（transport/context/model/interfaces/TODO）。
- 已完成：canonical `Message` schema、typed payload families、rich-media adapter codec 与回归测试。
- 已完成：主 specs 同步与 OpenSpec 归档。

## Evidence

### Commands
- `openspec list --json`
- `openspec new change "agentscope-d1-d3-message-pipeline"`
- `openspec status --change "agentscope-d1-d3-message-pipeline" --json`
- `openspec instructions proposal --change "agentscope-d1-d3-message-pipeline" --json`
- `openspec instructions design --change "agentscope-d1-d3-message-pipeline" --json`
- `openspec instructions specs --change "agentscope-d1-d3-message-pipeline" --json`
- `openspec instructions tasks --change "agentscope-d1-d3-message-pipeline" --json`
- `./.venv/bin/pytest -q tests/unit/test_context_message_types.py tests/unit/test_context_implementation.py tests/unit/test_transport_typed_payloads.py tests/unit/test_transport_types.py tests/unit/test_transport_channel.py tests/unit/test_transport_adapters.py tests/unit/test_base_agent_transport_contract.py tests/unit/test_five_layer_agent.py tests/unit/test_openrouter_adapter.py tests/unit/test_anthropic_model_adapter.py tests/unit/test_openai_model_adapter.py`
- `./.venv/bin/pytest -q tests/unit/test_context_message_types.py tests/unit/test_context_implementation.py tests/unit/test_context_compression.py tests/unit/test_transport_typed_payloads.py tests/unit/test_transport_types.py tests/unit/test_transport_channel.py tests/unit/test_transport_adapters.py tests/unit/test_base_agent_transport_contract.py tests/unit/test_five_layer_agent.py tests/unit/test_openrouter_adapter.py tests/unit/test_anthropic_model_adapter.py tests/unit/test_openai_model_adapter.py tests/unit/test_checkpoint_message_schema.py tests/unit/test_example_10_agentscope_compat.py tests/integration/test_hook_governance_flow.py`
- `git diff --check`
- `openspec validate --changes "agentscope-d1-d3-message-pipeline"`

### Results
- OpenSpec change 创建成功并完成归档（schema: `spec-driven`）。
- canonical `Message(role/kind/text/attachments/data)` 已在 context/model/session/memory/transport 主链路落地。
- rich-media `chat(text + images[])` 已进入 adapter serializer 与回归测试。
- focused/unit/integration regression suites passed。
- 文档与 specs 已同步，`git diff --check` 和 `openspec validate` 通过。

### Contract Delta
- `schema`: changed
  - transport 从 `payload: Any + event_type` 转为 typed payload。
  - canonical `Message` 从 `content: str` 转为 `role(MessageRole) + kind(MessageKind) + text + attachments(AttachmentRef[]) + data`。
- `error semantics`: changed
  - invalid typed payload / unsupported attachment-message_kind 组合改为 deterministic fail。
- `retry`: none
  - 本轮不调整运行时投递/重试机制。

### Golden Cases
- 新增：`openspec/changes/archive/2026-03-09-agentscope-d1-d3-message-pipeline/**`
- 更新：`docs/design/modules/transport/README.md`
- 更新：`docs/design/modules/context/README.md`
- 更新：`docs/design/modules/model/README.md`
- 更新：`docs/design/Interfaces.md`
- 更新：`docs/todos/agentscope_domain_execution_todos.md`
- 更新：`docs/todos/project_overall_todos.md`

### Regression Summary
- rich-media/context/transport/model focused suite passed。
- compatibility/example/integration suites covering canonical message migration passed。

### Observability and Failure Localization
- `start`: typed `MessagePayload(chat|thinking|tool_call|tool_result|summary)` enters context normalization
- `tool_call`: structured tool semantics come from `Message.data`
- `end`: adapters render canonical message into provider-native request blocks
- `fail`: none

### Structured Review Report
- module boundary:
  - transport 只负责 envelope 与 typed payload，不再承载 message 子语义。
  - context `Message` 作为唯一 canonical message。
  - model adapter 只消费 canonical `Message` 并输出 provider message。
- state:
  - 本 change 只完成 message schema，不引入 pending delta / prompt state / render cache。
- concurrency:
  - 主要风险在 `Message.content` 切除后的大面积调用点迁移。
- side-effect:
  - 属于明确 breaking change：移除 `event_type`、移除 `Message.content`、移除 raw transport payload compatibility。
- coverage:
  - transport/context/model/session/memory/adapter/example/integration 覆盖已补齐。

### Behavior Verification
- Happy path:
  - 单条 `chat` 消息可携带一段文字 + 多张图片，并保持为一个 logical user turn。
  - `tool_call/tool_result` 结构化语义从 `Message.data` 序列化到 adapter request。
- Error branch:
  - invalid typed payload / unsupported attachment-message kind 组合会在 schema validation 分支 deterministic fail。

### Risks and Rollback
- 风险：实现阶段需要同步改 transport/context/model/session/compression 多个模块。
- 风险：现有大量测试直接依赖 `Message.content` 与 `event_type`。
- 回滚：整体回退到旧消息契约；但当前工作区已按非兼容 cutover 前进，不再保留兼容层。

### Review and Merge Gate Links
- Intent PR: 待创建。
- Review request: 待创建实现 PR 后补充。
- Merge gate: 待实现与 CI 完成后补充。
