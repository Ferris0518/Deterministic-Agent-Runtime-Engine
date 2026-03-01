## 1. Execution Mode Activation

- [x] 1.1 在 `DareAgent` 中启用 `execution_mode` 分支选择逻辑。
- [x] 1.2 保持 `model_driven` 现有行为并补充兼容性断言。
- [x] 1.3 新增 `step_driven` 路径入口并接入 execute loop。

## 2. Step Executor Integration

- [x] 2.1 将 `IStepExecutor` 注入到 `DareAgent` 默认构建路径。
- [x] 2.2 在 `step_driven` 模式按 `ValidatedPlan.steps` 顺序执行。
- [x] 2.3 聚合 `StepResult` 与 `Evidence` 到统一 execute result 结构。
- [x] 2.4 实现 step 失败 fail-fast 与错误传播。

## 3. Plan-to-Step Bridge

- [x] 3.1 补齐无 validator 场景下的最小 step 转换逻辑。
- [x] 3.2 增加 step 合法性校验（capability、params、envelope 基础检查）。
- [x] 3.3 在 verify 阶段透传 plan 与 step 汇总信息。

## 4. Tests and Regression

- [x] 4.1 新增单测验证 step 顺序执行与失败中断语义。
- [x] 4.2 新增单测验证 evidence 聚合格式与字段完整性。
- [x] 4.3 新增集成测试覆盖 `step_driven` 完整链路（plan->execute->verify）。
- [x] 4.4 回归测试确保 `model_driven` 路径无行为退化。

## Evidence

- Runtime:
  - `dare_framework/agent/_internal/execute_engine.py`
  - `dare_framework/agent/dare_agent.py`
  - `dare_framework/agent/builder.py`
  - `dare_framework/agent/_internal/step_executor.py`
- Tests:
  - `tests/unit/test_dare_agent_step_driven_mode.py`
  - `tests/unit/test_dare_agent_orchestration_split.py`
- Commands:
  - `.venv/bin/pytest -q tests/unit/test_dare_agent_step_driven_mode.py tests/unit/test_dare_agent_orchestration_split.py` => `27 passed`
  - `.venv/bin/pytest -q` => `495 passed, 13 skipped, 1 warning`
- Consolidation note:
  - `add-step-driven-execute-loop` 的实现证据已并入本变更，作为同一能力切片的历史执行记录。
- Last Updated: `2026-03-01`
