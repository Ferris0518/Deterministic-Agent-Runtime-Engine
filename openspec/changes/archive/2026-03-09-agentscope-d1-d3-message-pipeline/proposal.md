## Why

当前 runtime 的消息主链路仍以纯字符串为中心：transport `kind=message` payload 要求是 `str`，context `Message` 也只支持 `content: str`。这导致“单条用户消息 = 一段文字 + 多张图片”无法以稳定 schema 进入模型调用链路，也让 `thinking/tool_call/tool_result/approval` 等语义继续分散在 event_type、metadata 和 ad-hoc payload 中。

现在需要先把消息格式基线收敛，形成 transport、context、model 三层一致的 canonical contract，为后续富媒体输入、adapter 能力探测和运行时缓存/resume 设计提供稳定前提。

## What Changes

- 将 transport 从 `payload: Any + event_type` 收敛为 typed payload 体系。
- 保留 `EnvelopeKind = message/select/action/control`，不再把消息子类型平铺到 envelope kind。
- 为 transport 定义统一 `EnvelopePayload` 抽象以及 `MessagePayload / SelectPayload / ActionPayload / ControlPayload` 四类 payload。
- **BREAKING**：升级 canonical `Message`，从 `content: str` 改为 `kind + text + attachments + data` 结构。
- 在 `Message(kind=chat)` 中支持 `text + image attachments[]`，覆盖“文字 + 多图片”组合消息。
- 将 `approval.pending / approval.resolved` 从 message event 迁回 `kind=select` 的 `ask / answered` 语义。
- **BREAKING**：移除 `TransportEventType` 作为主设计，业务语义改由 typed payload 承载。
- 明确 adapter 只消费 canonical `Message`，provider message 仅存在于 adapter 内部。

## Capabilities

### New Capabilities
- `rich-media-message-schema`: 定义 canonical `Message`、`AttachmentRef` 和 `kind=message` 的 typed payload 契约，支撑 `text + images[]` 组合消息进入 runtime/model 链路。

### Modified Capabilities
- `transport-channel`: transport envelope 从 content-agnostic Any payload 演进为 typed payload 家族，并把 approval/selection 语义归位到 `kind=select`。
- `chat-runtime`: runtime/context/model 调用链从 `Message.content: str` 演进为 canonical rich-media message，并要求 assemble/adapter 消费统一 message 契约。
- `interaction-dispatch`: deterministic interaction contract 需要显式纳入 `select` 路径与 approval ask/answered 语义，避免继续依赖 message event_type 变体。

## Impact

- Affected docs:
  - `docs/design/modules/transport/README.md`
  - `docs/design/modules/context/README.md`
  - `docs/design/modules/model/README.md`
  - `docs/design/Interfaces.md`
  - `docs/todos/agentscope_domain_execution_todos.md`
- Affected code:
  - `dare_framework/transport/*`
  - `dare_framework/context/*`
  - `dare_framework/model/*`
  - `dare_framework/agent/*`
  - `client/runtime/*`
  - `client/session_store.py`
- Breaking surface:
  - `TransportEnvelope` payload parsing
  - `context.Message` structure
  - adapter serialization contract
