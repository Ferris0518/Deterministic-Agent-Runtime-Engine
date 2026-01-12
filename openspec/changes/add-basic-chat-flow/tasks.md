## 1. Implementation
- [x] 1.1 Add `Config.workspace_roots` and propagate session config into `RunContext` for tool access.
- [x] 1.2 Add a prompt-aware context assembler and seed the default `InMemoryPromptStore` with the base English system prompt.
- [x] 1.3 Implement `OpenAIModelAdapter` using `langchain-openai`, mapping messages and tool calls to `ModelResponse`.
- [x] 1.4 Update `AgentRuntime` execute loop to call the model adapter, run tool calls via `ToolRuntime`, and emit a final response output.
- [x] 1.5 Implement `RunCommandTool` with workspace root enforcement and basic timeout handling.
- [x] 1.6 Add a minimal stdin/stdout chat example that wires the new adapter, prompt store, and command tool.
- [x] 1.7 Document dependency/setup notes for `langchain-openai` (README or example doc).

## 2. Validation
- [ ] 2.1 Manual smoke run of the stdin/stdout chat example (OpenAI key + simple prompt).
