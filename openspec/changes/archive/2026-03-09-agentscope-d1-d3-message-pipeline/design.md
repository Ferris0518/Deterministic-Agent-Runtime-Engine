## Context

当前消息主链路存在三处结构性问题：

1. transport `kind=message` 仍要求 `payload` 为纯字符串，导致协议层无法稳定承载富媒体输入或结构化消息。
2. context domain 的 `Message` 仍以 `content: str` 为中心，`thinking/tool_call/tool_result` 的结构化语义被迫散落在 `metadata`、`name` 和 ad-hoc 字符串编码中。
3. provider adapter 虽然各自已经有不同的消息序列化逻辑，但上游没有稳定的 canonical message contract，导致 transport、context、model 三层之间的边界持续模糊。

本次变更只解决“消息格式”问题，不解决运行时缓存、resume、增量投递和压缩状态机。运行时设计会在后续独立主题中处理。

## Goals / Non-Goals

**Goals:**

- 将 transport 从 `payload: Any + event_type` 收敛为 typed payload 体系。
- 保留现有 `EnvelopeKind = message/select/action/control`，避免 envelope 大类继续膨胀。
- 升级当前 `context.types.Message`，使其成为 framework 内部唯一 canonical message。
- 支持首版 `chat(text + images[])` 组合消息输入。
- 让 adapter 统一从 canonical `Message` 做 provider 序列化。
- 将 approval 交互从 message event 变回 `select` 语义。

**Non-Goals:**

- 不在本次设计中定义 `pending_delta / active_model_state / render cache`。
- 不处理富媒体完整模态矩阵；首版只要求图片附件。
- 不做兼容层或迁移适配器；本轮允许 breaking change。
- 不支持图文混排顺序表达。

## Decisions

### Decision: 保留 3 层，不新增平行 FrameworkMessage 类型

- 采用 3 层：
  - `TransportEnvelope`
  - typed `EnvelopePayload`
  - canonical `Message`
- 不新增 `FrameworkMessage` 新类型，直接升级现有 `Message`。

原因：

- 当前 `Message` 已经是 context/model/input 的核心类型，继续平行新增只会制造双重真相源。
- 文档和代码里大量 `Message(...)` 构造点都以它为 framework canonical message 使用，直接升级成本更可控。

备选方案：

- 方案 A：新增 `FrameworkMessage`，旧 `Message` 保持不动。
  - 不采用；会引入一轮无意义的双类型迁移。
- 方案 B：继续维持 `content: str`，把结构放到 `metadata`。
  - 不采用；会继续模糊 schema 和边界。

### Decision: `EnvelopeKind` 只保留协议大类，细粒度语义进入 payload

- 保留：
  - `message`
  - `select`
  - `action`
  - `control`
- `chat/thinking/tool_call/tool_result` 不进入 `EnvelopeKind`，只在 `MessagePayload.message_kind` 中表达。

原因：

- envelope.kind 负责 transport 路由，不负责会话语义。
- 这样既能保持 inbound routing 简洁，又不丢 message 子类型。
- 对于有限且确定性的 payload 子语义，优先使用强类型枚举而不是裸字符串，避免框架内部扩散硬编码常量。

备选方案：

- 方案 A：把 `chat/thinking/tool_call/tool_result` 平铺到 `EnvelopeKind`。
  - 不采用；会把协议层和消息语义层混在一起。

### Decision: 废弃 `event_type` 主设计，typed payload 成为唯一真相源

- `TransportEnvelope.event_type` 不再作为长期主设计。
- typed payload 上来后，消息/选择/动作/控制的业务语义只能由 payload 表达。

原因：

- `event_type` 与 payload subtype 并存会形成双重真相源。
- 当前 `approval.pending/resolved` 被塞进 `TransportEventType`，已经导致 approval 语义错误挂靠在 message/status 线上。

备选方案：

- 方案 A：继续保留 `event_type`，只把 payload 补强。
  - 不采用；长期会留下不可验证的一致性问题。

### Decision: `Message` 使用 `text + attachments + data`，不引入 `ChatBody`

canonical `Message` 字段收敛为：

- `id`
- `role`
- `kind`
- `text`
- `attachments`
- `data`
- `name`
- `metadata`
- `mark`

原因：

- `chat`、`thinking`、`summary` 都能直接复用 `text`。
- `chat`、后续可能的 `tool_result` 都能复用 `attachments`。
- `tool_call/tool_result` 通过 `data` 承载结构化字段。
- 不再需要专门的 `ChatBody`，结构更平。

备选方案：

- 方案 A：`Message.body` 做统一联合体。
  - 不采用；对当前目标来说抽象过重。
- 方案 B：仅使用 `text + attachments`，完全不要结构化字段。
  - 不采用；无法稳定表达 tool_call/tool_result。

### Decision: approval 归位到 `SelectPayload`

`SelectPayload` 负责：

- `select_kind = SelectKind.ASK | SelectKind.ANSWERED`
- `select_domain = SelectDomain.APPROVAL | SelectDomain.CHOICE | SelectDomain.FORM`

approval 的两个阶段分别映射：

- `approval.pending` -> `kind=select`, `select_kind=ask`, `select_domain=approval`
- `approval.resolved` -> `kind=select`, `select_kind=answered`, `select_domain=approval`

原因：

- approval 不是 message event，而是交互选择的一种。
- 现有 `EnvelopeKind.SELECT` 已经存在，语义上正好匹配。

补充约束：

- `MessagePayload.message_kind` 使用 `MessageKind` 枚举。
- `SelectPayload.select_kind` / `SelectPayload.select_domain` 使用 `SelectKind` / `SelectDomain` 枚举。
- `resource_action` 继续与 `ResourceAction` 对齐解析；是否强制为 enum 保留给后续扩展性评估。
- `control_id` 语义上与 `AgentControl` 对齐，后续实现不应继续散落硬编码字符串。

## Risks / Trade-offs

- [Breaking schema surface] transport / context / model 多处类型会同时改动
  → Mitigation：先改 docs 和 OpenSpec，再按 D1 -> D2 -> D3 切片实施。

- [测试面广] 当前大量测试直接断言 `Message.content`、`payload=str`、`event_type`
  → Mitigation：按模块迁移，优先修正 transport/context/model 三组 contract tests。

- [tool message 历史字段冲突] `name` 与 `data.tool_call_id` 可能并存一段时间
  → Mitigation：本次保留 `name`，但新结构化主语义以 `data` 为准。

- [adapter 能力差异] 不同 provider 对图片/tool blocks 的要求不同
  → Mitigation：provider message 仍留在 adapter 内部；当前 change 只冻结 canonical contract。

## Migration Plan

1. 先冻结 docs 设计基线与 OpenSpec 规格。
2. 在 transport domain 引入 typed payload，并把 approval 从 `event_type` 迁回 `select`。
3. 升级 canonical `Message` 与 `AttachmentRef`。
4. 调整 context `assemble()` 和 agent 输入链路，使 `kind=message` 的 payload 能归一化为 canonical `Message`。
5. 调整 model adapter 从 canonical `Message` 做 provider 序列化。
6. 同步更新 session/checkpoint/compression/test 契约。
7. 完成后再进入独立的“消息投递/缓存/压缩/resume/分发”设计切片。

Rollback:

- 由于本次允许 breaking change，不保留运行时双写兼容。
- 回滚以整体回退到旧 `TransportEnvelope + Message.content: str` 契约为准。

## Open Questions

- `Message.kind=tool_call/tool_result` 的 `data` 最小字段集是否需要在本 change 内完全冻结，还是只冻结承载位，细节留给后续工具链路切片。
- `SelectPayload.options/selected` 的最小标准化字段是否需要直接兼容当前 ask-user 工具输出。
- `TransportEnvelope.event_type` 是立即删除，还是实施阶段短暂保留为 deprecated 派生字段。
