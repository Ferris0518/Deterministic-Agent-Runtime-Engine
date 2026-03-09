## Why

The previous message-schema cutover established canonical `Message(text, attachments, data)`, but the runtime entry boundary still treated top-level input as `str`/`Task.description`. That leaves a contract hole: transport can carry `MessagePayload(chat + images[])`, yet the agent loop still collapses it to plain text before execution.

## What Changes

- **BREAKING** Promote canonical `Message` to a first-class agent input alongside `Task`.
- Add `Task.input_message` so orchestration keeps a separate execution description while preserving the original canonical user message.
- Convert transport-loop `MessagePayload` into canonical `Message` before agent execution instead of collapsing to `str`.
- Tighten canonical schema validation so `tool_call/tool_result` require structured `data`.
- Update client/example entry points to send `Message` rather than `Task(description=...)` for direct user prompts.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `rich-media-message-schema`: top-level agent/runtime input must preserve canonical `Message` rather than flattening to text.
- `transport-channel`: message envelopes reaching the agent loop must normalize into canonical `Message`.
- `session-loop`: session initialization must prefer `Task.input_message` over `Task.description` when constructing the first user turn.
- `plan-module`: `Task` gains canonical `input_message` for orchestration/message separation.

## Impact

- Affected code: `agent/*`, `plan/types.py`, `transport/*`, `client/runtime/task_runner.py`, active examples, message-schema tests.
- Affected APIs: `IAgent.__call__`, `IAgentOrchestration.execute`, `Task`.
- Systems: direct runtime entry, transport poll loop, session initialization, example/client CLIs.
