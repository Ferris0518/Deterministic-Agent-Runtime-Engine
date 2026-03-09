---
change_ids: ["agentscope-d5-safe-compression"]
doc_kind: feature
topics: ["agentscope", "compression", "context", "react-agent", "budget"]
created: 2026-03-02
updated: 2026-03-09
status: in_review
mode: openspec
---

# Feature: agentscope-d5-safe-compression

## Scope
补齐 AgentScope 迁移 D5：上下文压缩安全性与预算收敛能力，包括 tool-pair-safe、token-aware 触发与 ReAct 调用前自动压缩。

## OpenSpec Artifacts
- Proposal: `openspec/changes/agentscope-d5-safe-compression/proposal.md`
- Design: `openspec/changes/agentscope-d5-safe-compression/design.md`
- Specs:
  - `openspec/changes/agentscope-d5-safe-compression/specs/agentscope-safe-compression/spec.md`
  - `openspec/changes/agentscope-d5-safe-compression/specs/chat-runtime/spec.md`
- Tasks: `openspec/changes/agentscope-d5-safe-compression/tasks.md`

## Progress
- 已完成：D5 代码实现（tool-pair-safe、token-aware compression、ReAct pre-model auto-compress）。
- 已完成：OpenSpec tasks 全部打勾（10/10）。
- 已完成：PR #136 已合并到 `main`。
- 已完成：评审反馈处理与合并门禁记录闭环。
- 进行中：对 MovingCompressor 与 Context 集成进行语义修正：
  - 将 `Budget.max_tokens` 与压缩使用的 `max_context_tokens` 解耦，由调用方或 Context 上的 `context_window_tokens` 显式控制上下文窗口大小；
  - 压缩内部固定使用专用的摘要 prompt 与语言策略，不再透传外部系统 prompt / language；
  - 对跨分块产生的 tool_call/tool_result 拆分，仅在压缩层做「call 在 dropped 时将 result 一并并入 dropped」处理，其余结构问题留给上层诊断。

## Evidence

### Commands
- `openspec new change "agentscope-d5-safe-compression"`
- `openspec status --change "agentscope-d5-safe-compression" --json`
- `openspec instructions apply --change "agentscope-d5-safe-compression" --json`
- `/Users/lang/workspace/github/Deterministic-Agent-Runtime-Engine/.venv/bin/pytest -q tests/unit/test_context_compression.py tests/unit/test_react_agent_gateway_injection.py`
- `/Users/lang/workspace/github/Deterministic-Agent-Runtime-Engine/.venv/bin/pytest -q tests/unit/test_context_implementation.py tests/unit/test_agent_output_envelope.py tests/unit/test_example_10_agentscope_compat.py`
- `/Users/lang/workspace/github/Deterministic-Agent-Runtime-Engine/.venv/bin/pytest -q`

### Results
- OpenSpec change 创建成功（schema: spec-driven）。
- OpenSpec apply status：`10/10 tasks complete`（state=`all_done`）。
- D5 定向新增回归：`9 passed, 1 warning`。
- 受影响面回归：`38 passed, 1 warning`。
- 全量回归：`533 passed, 12 skipped, 1 warning`。

### Behavior Verification
- Happy path:
  - `compress_context(..., tool_pair_safe=True)` 可消除孤儿 `tool_result` 并修正无匹配的 `tool_call`；
  - `target_tokens` 生效时可在保留至少一条消息前提下收敛历史消息；
  - `ReactAgent(auto_compress=True)` 在模型调用前按预算阈值触发压缩。
- Error branch:
  - `ReactAgent(auto_compress=False)` 保持旧行为，不触发压缩调用；
  - 压缩后仍保留结构化 metadata 标记（`compressed + strategy`），便于诊断回滚。

### Risks and Rollback
- 风险：压缩触发时机变化可能影响部分场景回答质量。
- 风险：tool pair 保护逻辑若实现不严谨可能导致消息遗漏。
- 回滚：保持自动压缩开关可控，必要时回退到手动压缩路径。

### Review and Merge Gate Links
- Merge PR：`https://github.com/zts212653/Deterministic-Agent-Runtime-Engine/pull/136`
- Merge Commit：`https://github.com/zts212653/Deterministic-Agent-Runtime-Engine/commit/3b80d73e218cb67bd41056ce463040bec67e1cc1`
