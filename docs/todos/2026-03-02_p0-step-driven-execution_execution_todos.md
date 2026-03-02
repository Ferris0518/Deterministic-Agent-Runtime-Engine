# P0 Step-Driven Execution Execution TODO

> 日期：2026-03-02
> Change ID：`p0-step-driven-execution`
> 对应 OpenSpec：`openspec/changes/p0-step-driven-execution/`
> 状态：`active`

## 0. 使用规则

- 本文档是 `p0-step-driven-execution` 的 active execution board。
- 默认原则：`大包认领，小 task 验收`。
- `WP` 是认领单位；OpenSpec checkbox 只用于验收、回写、证据映射。
- 本板基于当前 OpenSpec `proposal.md`、`design.md`、`tasks.md` 生成，不在此处改写 change 范围。
- 初始 `Owner` 均为 `unassigned`；认领后再回写 owner、branch、PR、evidence。

## 1. 上下文与边界

- 目标：
  - 让 `execution_mode` 成为真实运行时开关。
  - 在 `step_driven` 模式下按 `ValidatedPlan.steps` 顺序执行，并产出结构化 `StepResult` 与 `Evidence`。
  - 让 `plan -> execute -> verify` 的输入输出闭环稳定可验证。
- 不在范围：
  - 不实现 DAG 并发 step 调度。
  - 不重写 planner 产出格式，只做最小转换与执行接线。
  - 不扩展复杂依赖表达式或 step 条件语言。
- 输入基线：
  - `openspec/changes/p0-step-driven-execution/proposal.md`
  - `openspec/changes/p0-step-driven-execution/design.md`
  - `openspec/changes/p0-step-driven-execution/tasks.md`
  - `docs/todos/project_overall_todos.md`（`T1-1`）
  - `docs/design/Architecture.md`

### 1.1 当前治理定位

| 项目项 | 当前表述 | 对应关系 |
|---|---|---|
| `T1-1` | 将 `ValidatedPlan.steps` 真正接入 Execute Loop | 本 execution board 的项目级路线图入口 |
| plan domain TODO | 扩展 step-driven 路径端到端覆盖 | 本 change 的设计补齐方向 |
| Architecture claim | step-driven 基线已落地，需补场景覆盖 | 本 change 负责从“基线可用”推进到“路径完整、证据稳定” |

## 2. Gate 冻结总览

| Gate | 冻结内容 | Producer | Consumer | 状态 | Evidence |
|---|---|---|---|---|---|
| Gate-1 | `execution_mode` 语义、前置条件、builder/agent 接线约定 | `WP-A` | `WP-B`, `WP-C`, `WP-D` | `todo` | 单测：模式切换、前置条件、默认兼容 |
| Gate-2 | `IStepExecutor` 调用契约、`StepResult`/`Evidence` 聚合格式、fail-fast 语义 | `WP-B` | `WP-C`, `WP-D` | `todo` | 单测：顺序执行、失败中断、字段完整性 |
| Gate-3 | `ProposedStep -> ValidatedStep` 最小转换、verify 输入结构、step 汇总字段 | `WP-C` | `WP-D` | `todo` | 单测：无 validator 转换、verify 透传、契约稳定 |
| Gate-4 | `plan -> execute -> verify` 端到端回归与 `model_driven` 非退化 | `WP-D` | 全体 | `todo` | 集成测试、回归测试、TODO/evidence 回写 |

## 3. Work Package 认领板

| WP | Goal | Owner | Depends On | Touch Scope | Freeze Gate | Status | Branch/Worktree | PR | Evidence | Last Updated |
|---|---|---|---|---|---|---|---|---|---|---|
| `WP-A` | 冻结运行时激活契约：`execution_mode` 分支、前置条件、builder/agent 接线 | `unassigned` | `-` | `dare_framework/agent/dare_agent.py`, `dare_framework/agent/builder.py`, `dare_framework/agent/_internal/execute_engine.py`, `tests/unit/test_dare_agent_step_driven_mode.py` | `Gate-1` | `todo` | `codex/p0-step-driven-wp-a` | `TBD` | 模式与前置条件单测、builder 接线证据 | `2026-03-02` |
| `WP-B` | 冻结 step 执行契约：顺序执行、结果聚合、fail-fast | `unassigned` | `Gate-1` | `dare_framework/agent/dare_agent.py`, `dare_framework/agent/_internal/step_executor.py`, `dare_framework/plan/interfaces.py`, `dare_framework/plan/types.py`, `tests/unit/test_dare_agent_step_driven_mode.py` | `Gate-2` | `todo` | `codex/p0-step-driven-wp-b` | `TBD` | step 执行与 evidence 聚合单测 | `2026-03-02` |
| `WP-C` | 冻结 plan-to-step / verify 桥接：最小转换、合法性校验、verify 透传 | `unassigned` | `Gate-1`, `Gate-2` | `dare_framework/agent/dare_agent.py`, `dare_framework/plan/interfaces.py`, `dare_framework/plan/types.py`, `tests/unit/test_dare_agent_step_driven_mode.py` | `Gate-3` | `todo` | `codex/p0-step-driven-wp-c` | `TBD` | bridge 与 verify 契约单测 | `2026-03-02` |
| `WP-D` | 完成回归与收口：step-driven 端到端、model-driven 非退化、证据回写 | `unassigned` | `Gate-2`, `Gate-3` | `tests/unit/test_dare_agent_step_driven_mode.py`, `tests/unit/test_five_layer_agent.py`, `tests/integration/test_example_agent_flow.py`, `openspec/changes/p0-step-driven-execution/tasks.md`, `docs/todos/project_overall_todos.md` | `Gate-4` | `todo` | `codex/p0-step-driven-wp-d` | `TBD` | 单测、集成测试、OpenSpec/TODO evidence | `2026-03-02` |

状态建议：

- `todo -> claimed -> doing -> review -> done`
- `todo/claimed/doing -> blocked -> doing/dropped`

## 4. 子任务验收表

### WP-A

范围说明：

- 负责把 `execution_mode` 从配置字段变成真实运行时分支。
- 明确 `step_driven` 的前置条件和错误边界，避免下游包在不稳定语义上并行开发。
- 这是整个 change 的第一个冻结点。

| Task ID | Related Gap / OpenSpec | Description | Status | Evidence |
|---|---|---|---|---|
| `A-1` | `T1-1 / 1.1` | 在 `DareAgent` 中启用 `execution_mode` 分支选择逻辑 | `todo` | 单测：`model_driven` / `step_driven` 选择 |
| `A-2` | `T1-1 / 1.2` | 保持 `model_driven` 现有行为并补充兼容性断言 | `todo` | 单测：默认路径无退化 |
| `A-3` | `T1-1 / 1.3` | 新增 `step_driven` 路径入口并接入 execute loop | `todo` | 单测：step path 实际进入 |
| `A-4` | `T1-1 / 2.1` | 将 `IStepExecutor` 注入到 `DareAgent` 默认构建路径 | `todo` | 单测：builder/agent 接线可观察 |

### WP-B

范围说明：

- 负责把 `IStepExecutor` 的执行语义冻结下来。
- 核心是“按顺序执行、收集证据、失败即停”，不在本包扩展重试或容错策略。

| Task ID | Related Gap / OpenSpec | Description | Status | Evidence |
|---|---|---|---|---|
| `B-1` | `T1-1 / 2.2` | 在 `step_driven` 模式按 `ValidatedPlan.steps` 顺序执行 | `todo` | 单测：顺序与 previous_results 传递 |
| `B-2` | `T1-1 / 2.3` | 聚合 `StepResult` 与 `Evidence` 到统一 execute result 结构 | `todo` | 单测：字段完整性与数量 |
| `B-3` | `T1-1 / 2.4` | 实现 step 失败 fail-fast 与错误传播 | `todo` | 单测：失败即停、错误稳定 |

### WP-C

范围说明：

- 负责把 planner 产物和 verify 输入接起来。
- 该包必须在 `Gate-2` 稳定后推进，避免聚合格式和 verify 结构来回漂移。

| Task ID | Related Gap / OpenSpec | Description | Status | Evidence |
|---|---|---|---|---|
| `C-1` | `T1-1 / 3.1` | 补齐无 validator 场景下的最小 step 转换逻辑 | `todo` | 单测：无 validator 仍可执行 step |
| `C-2` | `T1-1 / 3.2` | 增加 step 合法性校验（capability、params、envelope 基础检查） | `todo` | 单测：非法 step 被稳定拒绝 |
| `C-3` | `T1-1 / 3.3` | 在 verify 阶段透传 plan 与 step 汇总信息 | `todo` | 单测：verify 输入字段稳定 |

### WP-D

范围说明：

- 负责最终回归、集成验证和 evidence 回写。
- 不在此包重新定义运行时语义；此包消费前面 3 个 Gate 的冻结结果。

| Task ID | Related Gap / OpenSpec | Description | Status | Evidence |
|---|---|---|---|---|
| `D-1` | `T1-1 / 4.1` | 新增单测验证 step 顺序执行与失败中断语义 | `todo` | 单测通过 |
| `D-2` | `T1-1 / 4.2` | 新增单测验证 evidence 聚合格式与字段完整性 | `todo` | 单测通过 |
| `D-3` | `T1-1 / 4.3` | 新增集成测试覆盖 `step_driven` 完整链路（`plan -> execute -> verify`） | `todo` | 集成测试通过 |
| `D-4` | `T1-1 / 4.4` | 回归测试确保 `model_driven` 路径无行为退化 | `todo` | 回归测试通过 |

## 5. 接口兼容性矩阵

| 接口项 | 生产方 | 消费方 | 冲突风险 | 冻结时点 |
|---|---|---|---|---|
| `execution_mode` 语义 | `WP-A` | `WP-B`, `WP-C`, `WP-D` | 分支条件和前置约束不一致，导致下游在错误假设上开发 | `Gate-1` |
| builder -> agent step executor 接线 | `WP-A` | `WP-B` | builder 可配置但运行时未真正消费 | `Gate-1` |
| `IStepExecutor.execute_step(...)` 调用契约 | `WP-B` | `WP-C`, `WP-D` | previous results / return shape 不一致 | `Gate-2` |
| `StepResult` / `Evidence` execute result 聚合格式 | `WP-B` | `WP-C`, `WP-D` | verify 和测试断言无法稳定复用 | `Gate-2` |
| `ProposedStep -> ValidatedStep` 最小转换口径 | `WP-C` | `WP-D` | 无 validator 场景下 step 信息丢失或执行失败 | `Gate-3` |
| verify 输入中的 step 汇总字段 | `WP-C` | `WP-D` | validator 与测试看到的字段不一致 | `Gate-3` |

## 6. 强依赖关系

1. `WP-A` 必须先完成；这是所有下游包的运行时契约前提。
2. `WP-B` 依赖 `Gate-1`，因为 step executor 接线和执行入口都来自 `WP-A`。
3. `WP-C` 依赖 `Gate-2`，因为 verify 透传必须基于稳定的 `StepResult`/`Evidence` 聚合格式。
4. `WP-D` 最后收口，消费 `Gate-2` 和 `Gate-3` 的冻结结果做端到端验证与 evidence 回写。

## 7. 联调与收口

- 联调入口：
  - `tests/unit/test_dare_agent_step_driven_mode.py`
  - `tests/unit/test_five_layer_agent.py`
  - `tests/integration/test_example_agent_flow.py`
- 完成条件：
  - `Gate-1`、`Gate-2`、`Gate-3` 均有冻结证据。
  - `step_driven` 链路能稳定完成 `plan -> execute -> verify`。
  - `model_driven` 默认路径无行为退化。
  - `openspec/changes/p0-step-driven-execution/tasks.md` 与相关 TODO evidence 完成回写。

## 8. 维护约定

- 认领发生变化时，同步回写 `Owner`、`Status`、`Branch/Worktree`、`PR`、`Last Updated`。
- 若实现中发现 OpenSpec 设计与代码现状不一致，先补 design/gap，不直接在代码层继续扩散。
- `review` 前必须补测试或集成 evidence。
- `done` 前必须确认 execution board 与 OpenSpec `tasks.md` 状态一致。
