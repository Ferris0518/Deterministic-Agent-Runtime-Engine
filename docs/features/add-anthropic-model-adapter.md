---
change_ids: ["add-anthropic-model-adapter"]
doc_kind: feature
topics: ["model", "anthropic", "adapter", "cli-doctor"]
created: 2026-03-05
updated: 2026-03-05
status: draft
mode: openspec
---

# Feature: add-anthropic-model-adapter

## Scope
新增独立 `AnthropicModelAdapter`，对接 Anthropic 官方 Messages API，并在 runtime/CLI 侧完成 `anthropic` adapter 的加载与诊断接入，不改造既有 OpenAI/OpenRouter adapter 内部实现。

## OpenSpec Artifacts
- Proposal: `openspec/changes/add-anthropic-model-adapter/proposal.md`
- Design: `openspec/changes/add-anthropic-model-adapter/design.md`
- Specs:
  - `openspec/changes/add-anthropic-model-adapter/specs/anthropic-model-adapter/spec.md`
- Tasks: `openspec/changes/add-anthropic-model-adapter/tasks.md`

## Progress
- 已完成：Anthropic adapter 代码、manager 接入、CLI doctor 接入、依赖与文档更新。
- 已完成：定向单测回归通过。
- 待完成：评审链接与归档动作。

## Evidence

### External References
- Anthropic Messages API: `https://docs.anthropic.com/en/api/messages`
- Anthropic tool use examples: `https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview`
- OpenRouter Anthropic Opus model page: `https://openrouter.ai/anthropic/claude-opus-4.1`
- OpenRouter Anthropic Sonnet model page: `https://openrouter.ai/anthropic/claude-sonnet-4.5`

### Commands
- `openspec new change "add-anthropic-model-adapter"`
- `openspec status --change "add-anthropic-model-adapter" --json`
- `.venv/bin/pytest -q tests/unit/test_anthropic_model_adapter.py tests/unit/test_default_model_adapter_manager.py tests/unit/test_client_cli.py`

### Results
- OpenSpec change 创建成功（schema: `spec-driven`）。
- Anthropic adapter 目标测试集通过：`58 passed, 1 warning`。

### Contract Delta
- schema: `changed`（新增 `anthropic` adapter 选择与请求/响应规范化行为，模型名为配置直传）。
- error semantics: `changed`（`anthropic` SDK 缺失时新增明确错误提示）。
- retry: `none`（未新增重试语义）。

### Golden Cases
- `tests/unit/test_anthropic_model_adapter.py`
- `tests/unit/test_default_model_adapter_manager.py`
- `tests/unit/test_client_cli.py`

### Regression Summary
- 定向回归通过，覆盖新增 adapter 的序列化、模型名直传、manager 选择与 CLI doctor 诊断分支。

### Observability and Failure Localization
- 入口：`DefaultModelAdapterManager.load_model_adapter(config)`。
- tool_call/tool_result 序列化：`AnthropicModelAdapter._serialize_system_and_messages`。
- 响应解析：`_extract_response_text` / `_extract_tool_calls` / `_extract_usage`。
- 失败定位：`_build_client`（依赖缺失）、`build_doctor_report`（依赖与 API key 诊断）。

### Structured Review Report
- module boundary: 仅新增 Anthropic adapter 模块并修改最小接入面（manager/export/doctor）。
- state: 无新增全局可变状态，client 延续 lazy client 初始化。
- concurrency: 复用 async client 调用模型 API，不引入并发共享写路径。
- side-effect: 新增外部依赖 `anthropic`，其余 side-effect 不变。
- coverage: 新增/修改行为均有对应单测。

### Behavior Verification
- Happy path:
  - `adapter=anthropic` 时可加载 Anthropic adapter 并完成消息/工具块序列化与响应归一化。
  - 显式模型名（例如 `claude-sonnet-4-5`）会原样透传到 Anthropic SDK。
- Error branch:
  - 缺少 `ANTHROPIC_API_KEY` 或 `api_key` 时抛出显式错误。
  - 缺少 `Config.llm.model` 且 `ANTHROPIC_MODEL` 未设置时抛出模型必填错误。
  - doctor 在 `adapter=anthropic` 且未安装 `anthropic` SDK 时输出依赖告警。

### Risks and Rollback
- 风险：运行配置缺少模型名会导致 adapter 初始化失败。
- 回滚：删除 `anthropic` 分支与新增 adapter 文件即可恢复至原行为，不影响 OpenAI/OpenRouter 路径。

### Review and Merge Gate Links
- Review request: 待创建 PR 后补充。
- Merge gate: 待 CI 与 reviewer 通过后补充。
