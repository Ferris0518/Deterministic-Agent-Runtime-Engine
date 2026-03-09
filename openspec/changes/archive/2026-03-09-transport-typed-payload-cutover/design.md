## Context

`agentscope-d1-d3-message-pipeline` 已经完成 canonical `Message` 与 transport typed payload 基线，但 transport 运行时仍保留三层历史兼容：

1. `TransportEnvelope.event_type` 仍承担 reply 语义分派，和 typed payload 并行存在。
2. `EnvelopeKind.MESSAGE/ACTION/CONTROL` 仍允许裸 `str` / 裸 `dict` payload 进入 runtime。
3. client/example/test 仍大量围绕 `dict payload + event_type` 解析结果，而不是按 payload family 处理。

这让 envelope `kind`、payload schema、reply semantics 三者没有真正收敛，也继续放大维护成本。

## Goals / Non-Goals

**Goals:**
- 删除 transport 主设计中的 `event_type`，不再把 reply 语义挂在 envelope 附加字符串上。
- 删除 message/action/control 的 legacy raw payload 兼容，只接受 typed payload。
- 让 success/error/result 语义回收到 `MessagePayload/ActionPayload/ControlPayload/SelectPayload` 自身。
- 更新 runtime/client/example/tests，使 typed payload 成为唯一 transport 契约。

**Non-Goals:**
- 不修改 canonical `Message` schema。
- 不处理 pending delta / cache / resume 等运行时状态设计。
- 不新增 `status` / `error` 之类的 envelope kind。

## Decisions

### Decision: `TransportEnvelope` 只保留 `kind + payload`

删除 `event_type` 字段。reply 分派完全由 `EnvelopeKind` 与 payload 家族决定。

原因：
- `kind + event_type + payload` 是三套并行语义源。
- typed payload 已经足够表达请求和响应的结构化语义。

替代方案：
- 保留 `event_type` 作为 deprecated 字段。
  - 不采用；仍会继续扩散分支判断和旧测试口径。

### Decision: typed payload 自身承接请求/响应双态

- `MessagePayload`
  - 请求：`role=user`, `message_kind=chat`
  - 响应：`role=assistant`, `message_kind=chat|thinking|tool_call|tool_result|summary`
  - 错误：使用 `text + data{success/code/reason/...}` 表达
- `ActionPayload`
  - 请求：`resource_action + params`
  - 响应：`resource_action + ok/result/code/reason`
- `ControlPayload`
  - 请求：`control_id + params`
  - 响应：`control_id + ok/result/code/reason`
- `SelectPayload`
  - 保持 `ask|answered`

原因：
- 不引入新的 envelope kind。
- 请求和响应都保留在同一协议家族中，client 侧处理更稳定。

替代方案：
- 用 `kind=message` 包一个统一 dict reply。
  - 不采用；会重新引入 dict payload 弱结构。

### Decision: message request error 也回到 `MessagePayload`

message 请求失败时返回：
- `kind=message`
- `payload=MessagePayload(role=assistant, message_kind=summary, text=<reason>, data={success:false, code, reason, target})`

原因：
- 保持“消息请求得到消息回复”的对称性。
- 不需要单独的 error envelope kind。

替代方案：
- message error 走 `control` 或 `action` reply。
  - 不采用；语义错位。

### Decision: transport JSON adapters 只做 typed payload 序列化/反序列化

WebSocket/stdio/direct adapters 保留“dataclass <-> JSON dict”的转换，但不再接受语义上的 raw string payload。

原因：
- JSON over-the-wire 和 runtime typed payload 并不冲突。
- 需要保留网络边界的反序列化能力，但不保留 runtime 的 legacy schema。

## Risks / Trade-offs

- [Breaking transport consumers] 现有 example/测试/CLI 解析将失效
  → Mitigation：同一 change 内同步更新 adapters、client helpers、tests。

- [Error semantics drift] message error 不再通过 `event_type=error` 判断
  → Mitigation：统一 `MessagePayload.data.success/code/reason` 结构，并增加 error-path tests。

- [Hook observability coupling] 现有 hook transport 事件依赖 `event_type`
  → Mitigation：改为 `kind=message + MessagePayload.message_kind/data`，hook tests 同步切换。

## Migration Plan

1. 更新 transport/context/model 文档，冻结 typed-reply cutover 设计。
2. 修改 `TransportEnvelope` 与 default channel/dispatcher，移除 raw payload/event_type 兼容。
3. 修改 agent transport loop 与 hook transport emitter，改发 typed replies。
4. 修改 client/example/adapters/tests，切换为 typed payload 解析。
5. 跑 transport/runtime/example 回归并完成 OpenSpec 证据回写。

Rollback:
- 该 change 明确允许 breaking change；如需回退，整体回退到引入 typed replies 前的 `event_type + dict payload` 契约。

## Open Questions

- `MessagePayload.data` 的最小 reply 字段集是否需要进一步抽为共享 helper，还是先在 transport/runtime 内按约定使用。
