# Example 08: Plan Agent (plan_v2)

验证 plan_v2 的 Planner 效果：用 ReactAgent + `with_plan_provider(Planner(state))` 组成只做规划的 Plan Agent，跑完一次任务后打印 `PlannerState` 和 `copy_for_execution()`。

## 运行

```bash
export OPENROUTER_API_KEY=your_key
python main.py
# 或自定义任务描述
python main.py "Plan how to add a new API endpoint that returns JSON."
```

依赖：`OPENROUTER_API_KEY`；可选 `OPENROUTER_MODEL`（默认 `openai/gpt-4o-mini`）、`OPENROUTER_MAX_TOKENS`（默认 2048）。

## 预期

- 模型会调用 `create_plan`、`validate_plan` 等工具。
- 终端会打印规划结果：`plan_description`、`steps`、以及 `copy_for_execution()` 的摘要。
