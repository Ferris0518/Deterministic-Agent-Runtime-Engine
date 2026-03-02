# Spec-Driven 协作粒度设计

> 日期：2026-02-28
> 状态：adopted
> 适用范围：4 人并行、spec-driven、多人同时推进多个 active changes 的场景

## 1. 背景

当前仓库已经具备文档先行治理闭环：

- `docs/design/**` 作为权威设计
- `docs/todos/*_gap_analysis.md` 作为设计-实现差异分析
- `docs/todos/*_todo.md` 作为治理清单
- `openspec/changes/<change-id>/*` 作为变更执行工件

问题不在于“缺少 TODO”，而在于多人并行时缺少统一的认领粒度与冻结边界：

- `docs/design/TODO_INDEX.md` 适合看 backlog，不适合做认领板。
- `docs/todos/project_overall_todos.md` 适合记录项目路线图，不适合承载单个 feature 的细节认领。
- 当多人直接按 bullet 或文件认领时，容易在共享接口、共享核心文件和共享语义上发生冲突。

## 2. 设计目标

本设计希望同时满足：

1. 保持 vibe coding 的高吞吐，不把任务拆得过碎。
2. 在共享契约处建立足够强的冻结边界，降低返工。
3. 保留细粒度验收证据，避免“大包做完却无法 review”。
4. 继续遵循“文档更新 -> gap 分析 -> TODO -> OpenSpec -> 回写/归档”的治理闭环。

## 3. 核心决策

### 3.1 三层协作板

- `docs/design/TODO_INDEX.md`
  - 角色：设计 backlog / 发现池
  - 作用：回答“还有哪些设计 TODO”
  - 不负责：认领、依赖编排、PR 跟踪

- `docs/todos/project_overall_todos.md`
  - 角色：项目路线图 + 外层 `Claim Ledger`
  - 作用：回答“当前项目级优先级是什么”以及“哪一段 TODO scope 当前由谁推进”
  - 不负责：单个 change 内部的 work package 施工细节

- `docs/todos/YYYY-MM-DD_<change-id>_execution_todos.md`
  - 角色：active change 内层执行协作板
  - 作用：回答“这一 change 内部谁在做什么、依赖谁、冻结到哪一层、证据在哪里”
  - 它承载 work package 协调，但不替代外层 `Claim Ledger`

### 3.2 认领粒度

默认原则：`外层认领 scope，内层拆 work package，小 task 验收`。

- 外层认领单位是 `TODO scope` 或 `change scope`
- 内层协作单位是 `work package`
- 验收单位是 task / OpenSpec checkbox / gap 映射项

`work package` 的定义：

- 一个 owner 独占
- 一个主要目标
- 推荐在 `0.5-2` 天内闭环
- 最多跨 1 个 Gate
- 能独立给出联调或测试证据

不建议的认领方式：

- 直接按单个 bullet 抢任务
- 一个人认领整个大模块
- 两个人同时自由修改同一组共享契约

### 3.3 Gate 冻结

共享契约必须先冻结再并行，包括但不限于：

- schema
- payload shape
- message / event type
- plan state 语义
- policy decision 结构
- 日志主字段与审计字段

因此，一个 active change 的流程应为：

1. 先写外层 `Claim Ledger`
2. 再提交 docs-only `spec-sync / intent PR`
   内容包含：设计文档、gap analysis、execution board、OpenSpec artifacts
3. `intent PR` 合入后，work package 才允许进入 `claimed/doing`
4. Gate 冻结完成后，下游包再并行实现

## 4. 数据结构

execution board 的 `work package` 记录至少包含：

| 字段 | 含义 |
|---|---|
| `WP` | work package 唯一标识 |
| `Goal` | 独立目标 |
| `Owner` | 唯一负责人 |
| `Depends On` | 上游包或 Gate |
| `Touch Scope` | 预计改动目录/文件 |
| `Freeze Gate` | 本包依赖或产出的冻结边界 |
| `Status` | `todo/claimed/doing/review/blocked/done/dropped` |
| `Branch/Worktree` | 开发分支或工作树 |
| `PR` | 对应 PR |
| `Evidence` | 测试、联调、文档回写证据 |
| `Last Updated` | 最后更新时间 |

子任务记录至少包含：

| 字段 | 含义 |
|---|---|
| `Task ID` | 任务唯一标识 |
| `Related Gap / OpenSpec` | 对应 gap 或 OpenSpec task |
| `Description` | 具体验收点 |
| `Status` | 任务状态 |
| `Evidence` | 证据链接 |

## 5. 关键接口

人与文档的接口：

- 从 `TODO_INDEX` 发现候选方向
- 从 `project_overall_todos.md` 确认优先级
- 从 `execution_todos.md` 认领具体 work package
- 从 `openspec/changes/<change-id>/tasks.md` 验收与回写

PR 与认领板的接口：

- 每个 PR 必须标注 `change-id` 与 `WP`
- `review` 之前必须回写 execution board
- `done` 之前必须同步回写 OpenSpec `tasks.md`

## 6. 错误处理与例外

- 如果一个 `work package` 在 24 小时内没有实际推进，应从 `claimed` 释放回 `todo` 或改为 `blocked`。
- 如果实现中发现 Gate 未冻结，不得继续扩散实现，应先回到 spec-sync 修正文档。
- 如果一个包跨越两个以上 Gate，必须拆分，否则极易形成设计漂移和代码冲突。
- 生产止血类紧急修复可先做最小改动，但仍需在 24 小时内补 execution board 与文档闭环。

## 7. 采纳结果

本设计通过以下文档落地：

- `docs/todos/README.md`
- `docs/guides/Team_Agent_Collab_Playbook.md`
- `docs/todos/templates/change_execution_todo_template.md`

后续所有 active changes 应优先复用统一模板，而不是临时自由发挥。
