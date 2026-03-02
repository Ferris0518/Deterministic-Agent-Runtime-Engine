---
change_ids: ["p0-step-driven-execution"]
doc_kind: feature
topics: ["execution-mode", "step-driven", "plan-execute-verify"]
created: 2026-03-01
updated: 2026-03-01
status: done
mode: openspec
---

# Feature: p0-step-driven-execution

## Scope
将 `ValidatedPlan.steps` 从“描述性数据”升级为可执行主链路，打通 `execution_mode` 的 `step_driven` 路径，并保持 `model_driven` 默认行为兼容。

## OpenSpec Artifacts
- Proposal: `openspec/changes/p0-step-driven-execution/proposal.md`
- Design: `openspec/changes/p0-step-driven-execution/design.md`
- Specs:
  - `openspec/changes/p0-step-driven-execution/specs/session-loop/spec.md`
  - `openspec/changes/p0-step-driven-execution/specs/core-runtime/spec.md`
  - `openspec/changes/p0-step-driven-execution/specs/step-driven-execution/spec.md`
  - `openspec/changes/p0-step-driven-execution/specs/plan-module/spec.md`
- Tasks: `openspec/changes/p0-step-driven-execution/tasks.md`

## Consolidation
- 本 change 作为 step-driven 能力的唯一 P0 主线。
- 历史并行 change `add-step-driven-execute-loop` 的实现证据并入本 change。

## Evidence

### Commands
- `openspec status --change p0-step-driven-execution --json`
- `.venv/bin/pytest -q tests/unit/test_dare_agent_step_driven_mode.py tests/unit/test_dare_agent_orchestration_split.py`
- `.venv/bin/pytest -q`

### Results
- OpenSpec status: `isComplete=true`（proposal/design/specs/tasks 均为 `done`）。
- 定向回归：`27 passed`。
- 全量回归：`495 passed, 13 skipped, 1 warning`。

### Behavior Verification
- Happy path: `execution_mode="step_driven"` 时按 `ValidatedPlan.steps` 顺序执行，并产出聚合输出。
- Error branch: 缺失 validated plan / 空 steps / step 失败时，执行链路 fail-fast 并返回结构化错误。
- Compatibility: 未配置执行模式时保持 `model_driven` 行为不变。

### Risks and Rollback
- 风险：双执行模式长期并存会增加维护成本。
- 回滚：将运行时配置回退为 `model_driven`，并禁用 step-driven 路径入口。

### Review and Merge Gate Links
- Pending in current branch（待提交 PR 后补充链接）。
