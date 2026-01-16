# DARE Framework：架构现状与优先级清单（以代码实现为准）

> 目的：用“实现视角”快速解释项目是怎么拼起来的，并给出一份可执行的优先级 TODO（带完成勾选）。
>
> 状态来源：代码目录结构 + `openspec list` / `openspec/changes/*/tasks.md`（最后更新：2026-01-15）。

## 1. 架构现状（实现视角）

### 1.1 分层与目录职责

- `dare_framework/core/`：协议（Protocol/Interface）+ 数据模型（`core/models/*`）+ 运行时引擎（`core/runtime_engine.py`）
- `dare_framework/components/`：默认组件实现（EventLog/Checkpoint/ToolRuntime/PlanGenerator/ModelAdapter/Hook/Validator 等）
- `dare_framework/composition/`：组装与插件发现（`AgentBuilder`、`ComponentManager`、entry points）
- `examples/`：可运行示例（例如 stdin/stdout chat）
- `tests/`：单元/集成测试

### 1.2 关键运行链路（从 build 到 RunResult）

1. `AgentBuilder.build()`/`build_async()` 组装 `AgentRuntime`（`dare_framework/core/runtime_engine.py`）
2. `Agent.run(task, deps)` → `runtime.init(task)` → `runtime.run(task, deps)`
3. `AgentRuntime.run()` 创建 `SessionContext`（携带有效 `Config`），将 Task 拆成 Milestones 执行
4. 每个 Milestone 进入闭环：
   - **Plan Loop**：`IContextAssembler.assemble()` → `IPlanGenerator.generate_plan()` → `IValidator.validate_plan()`
   - **Execute Loop**：
     - 未配置 `IModelAdapter`：按已验证计划逐步调用工具（plan-driven）
     - 配置了 `IModelAdapter`：进入 model tool-call 循环（model-driven）
   - **Verify/Remediate**：`IValidator.validate_milestone()` 失败后由 `IRemediator.remediate()` 产出 reflection 并重试
5. 所有工具执行统一通过 `ToolRuntime.invoke()`，并可选进入 **Tool Loop**（Envelope/DonePredicate + 证据校验）

### 1.3 状态、审计与可观测性

- 事件日志：`LocalEventLog` 追加写入 `.dare/event_log.jsonl`，维护 `prev_hash`/`event_hash` 形成 hash-chain（审计/WORM 基础）
- 快照：`FileCheckpoint` 写入 `.dare/checkpoints/*.json`（为跨 context window 预留）
- Hooks：`AgentRuntime._log_event()` 对每个 `Event` 调用 `IHook.on_event()`；Hook 异常会写入 `hook.error` 事件
- 终端可观测：`StdoutHook` 将 runtime/plan/model/tool 关键事件格式化输出

### 1.4 配置与插件扩展点

- 配置模型：`dare_framework/core/models/config.py` → `Config`（`llm/mcp/tools/allowtools/allowmcps/components/workspace_roots`）
- 配置来源：`IConfigProvider`（当前默认 `StaticConfigProvider`），支持 `current()` + `reload()`
- 组件发现：`dare_framework/composition/component_manager.py` 通过 Python entry points 加载：
  - validators / memory / model_adapters / tools / skills / mcp_clients / hooks / config_providers / prompt_stores
- 组件开关：`Config.components` 支持按 `ComponentType + component_name` 禁用组件；工具可通过 `RunContext.config.workspace_roots` 约束执行范围（`RunCommandTool`）

## 2. 优先级清单（Checklist）

> 优先级默认按“阻塞程度/对可运行性影响”排序；如果你们有明确里程碑，可直接调整本节顺序。

### P0（必须）：保证核心链路可跑通、可验证

- [ ] `hierarchical-config-management`：执行并确认受影响测试通过（`openspec/changes/hierarchical-config-management/tasks.md` 3.3）
- [ ] `add-runtime-config-model`：补齐分层 runtime 配置模型/合并规则/会话注入/组件选择（`openspec/changes/add-runtime-config-model/tasks.md` 1.1 ~ 3.2）
- [ ] 修复 `BaseComponentManager.load()` 中 `config_provider` 未定义导致的加载路径异常（`dare_framework/composition/component_manager.py`）

### P1（应该）：让示例链路可复现、可回归

- [ ] `add-basic-chat-flow`：手动 smoke run stdin/stdout chat 示例（`openspec/changes/add-basic-chat-flow/tasks.md` 2.1）
- [ ] `add-basic-chat-flow`：补 stdout hook 的单测覆盖（`openspec/changes/add-basic-chat-flow/tasks.md` 2.2）

### 已完成（来源：`openspec list`）

- [x] `add-dare-framework-foundation`
- [x] `refactor-layered-structure`
- [x] `refactor-component-managers`
- [x] `refine-component-manager-config`
- [x] `add-component-manager-entrypoints`

## 3. 相关“权威设计”文档入口（阅读顺序）

1. `openspec/project.md`（项目上下文/约束/架构总览）
2. `doc/design/Architecture_Final_Review_v1.3.md`（架构终稿）
3. `doc/design/Interface_Layer_Design_v1.1_MCP_and_Builtin.md`（接口层设计）
