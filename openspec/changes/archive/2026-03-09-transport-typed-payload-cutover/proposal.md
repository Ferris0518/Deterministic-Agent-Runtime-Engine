## Why

当前 transport 主链路虽然已经引入 typed payload，但运行时仍保留多层 legacy 兼容：`EnvelopeKind.MESSAGE/ACTION/CONTROL` 仍接受裸字符串或裸字典，reply 侧仍依赖 `event_type + dict payload` 包装，导致协议层存在双重真相源，client/example/test 也持续分叉。

消息格式切片已经完成，这个兼容壳现在反而阻碍 transport、agent loop、client 消费方彻底收敛到 typed payload 契约，因此需要单独做一次 non-compatible cutover。

## What Changes

- **BREAKING** 删除 `TransportEnvelope.event_type` 作为 transport 主设计字段，reply 语义改由 typed payload 家族自身表达。
- **BREAKING** 删除 `EnvelopeKind.MESSAGE/ACTION/CONTROL` 对裸 `str` / 裸 `dict` payload 的接收与分派兼容，只保留 typed payload。
- 将 agent transport loop 的成功/失败回复改为 typed payload：
  - `message` 请求回复 `MessagePayload`
  - `action` 请求回复 `ActionPayload`
  - `control` 请求回复 `ControlPayload`
  - `select` 保持 `SelectPayload`
- 更新 stdio/websocket/direct client adapters、dispatcher、example CLI 和相关测试，统一消费 typed payload。

## Capabilities

### New Capabilities
- `typed-transport-replies`: transport reply envelopes use typed payloads instead of `event_type + dict payload`

### Modified Capabilities
- `transport-channel`: inbound/outbound envelope validation and routing become typed-payload-only
- `interaction-dispatch`: action/control dispatch contracts stop accepting legacy string payloads
- `chat-runtime`: agent transport loop returns canonical assistant message payloads and typed error/result envelopes

## Impact

- Affected code:
  - `dare_framework/transport/types.py`
  - `dare_framework/transport/_internal/default_channel.py`
  - `dare_framework/transport/_internal/adapters.py`
  - `dare_framework/transport/interaction/dispatcher.py`
  - `dare_framework/transport/interaction/payloads.py`
  - `dare_framework/agent/base_agent.py`
  - `dare_framework/agent/react_agent.py`
  - `dare_framework/hook/_internal/agent_event_transport_hook.py`
  - client/example consumers using `DirectClientChannel.ask()` or raw transport events
- Affected APIs:
  - transport envelope schema
  - transport reply parsing in client/example code
  - action/control request construction in tests/examples
