# Change: Add basic chat flow with prompts, OpenAI adapter, and local command tool

## Why
We need a minimal, usable chat flow that exercises the core framework loops without premature complexity. This enables a first agent client (stdin/stdout), a base prompt, and an OpenAI adapter via LangChain while keeping other plugins as no-op.

## What Changes
- Add a default English base system prompt stored in the default prompt store.
- Introduce an OpenAI model adapter built on `langchain-openai` and wired into the runtime loop.
- Provide a local command tool with workspace root restrictions for write operations.
- Add a minimal stdin/stdout chat client example to demonstrate a basic conversation.
- Extend runtime/config plumbing so tools can access `workspace_roots` from session config.

## Impact
- Affected modules: `dare_framework/core`, `dare_framework/components`, `dare_framework/composition`, `examples/`.
- New dependency: `langchain-openai` (and its `langchain-core` dependency).
- No backward-compat requirement (early-stage framework).
