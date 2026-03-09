## Overview

This change closes the remaining gap between the canonical message schema and the runtime execution boundary. The framework already stores and serializes canonical `Message(role, kind, text, attachments, data)`, but direct execution and transport polling still flatten top-level input to strings. The design goal is to make canonical `Message` the first-class user input while keeping `Task` as an orchestration object.

## Architecture

### Entry boundary

- `IAgent.__call__` accepts `str | Message`.
- `IAgentOrchestration.execute` receives canonical `Message`.
- `Message` is the preferred direct prompt input.
- `Task` remains the five-layer orchestration carrier and may optionally hold `input_message`.

### Orchestration boundary

- `Task.description` remains a planning/execution description.
- `Task.input_message` becomes the source of truth for the canonical first user turn.
- When `Task.input_message` is absent, runtime derives a default `Message(role=user, kind=chat, text=description)`.

### Transport boundary

- `TransportEnvelope(kind=message, payload=MessagePayload)` normalizes into canonical `Message` before agent execution.
- The transport loop must not drop `attachments` or `data`.

## Data Structures

### Task

```text
Task
- description: str
- input_message: Message | None
- milestones / metadata / previous_session_summary / resume_from_checkpoint
```

### Validation

- `Message.kind in {tool_call, tool_result}` requires non-empty `data`.
- `thinking/summary/tool_call` reject attachments.

## Workflow

1. Direct caller or transport provides a top-level prompt.
2. Agent normalizes the input:
   - `Message` passes through unchanged.
   - `str` is upgraded at the public agent boundary to `Message(role=user, kind=chat, text=...)`.
3. Session loop adds the normalized canonical user message to STM.
4. Model adapters receive assembled canonical `Message` objects without earlier text flattening.

## Error Handling

- Invalid top-level transport message payload remains a deterministic transport error.
- Invalid canonical messages (for example `tool_call` without `data`) fail at schema construction time.

## Testing

- Transport loop preserves attachments when polling `MessagePayload`.
- Session loop prefers `Task.input_message`.
- Canonical schema rejects `tool_call/tool_result` without `data`.
- Example/client helpers send `Message` rather than `Task(description=...)`.
