<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# DARE Framework - AI Agent Guide

> DARE (Deterministic Agent Runtime Engine) - 面向高安全性、可审计性和多 Agent 协作场景的工业级 AI Agent 执行框架。

## Project Overview

### Purpose

DARE Framework 是一个用于构建不同类型 Agent Runtime 的框架，而非交付某个具体 Agent 产品。核心目标场景包括：

1. **银行/金融场景** - 强审计、合规、人在回路（Human-in-the-loop）
2. **代码生成场景** - 容错、迭代、外部验证
3. **多 Agent 协作** - 任务租约、冲突处理、统一状态

### Core Design Principles

| 原则 | 含义 |
|-----|-----|
| **状态外化** | 所有状态存 EventLog/DB，不依赖模型记忆 |
| **LLM 不可信** | Plan 产出只是"意图"，安全关键字段从可信源派生 |
| **外部可验证** | "完成"由外部验证器判定，不信任模型说"done" |
| **增量执行** | 每步做完提交，留清晰交接物 |
| **可审计** | 每个决策有结构化记录 + 证据链 |

## Technology Stack

- **Primary Language**: Python 3.12+ (项目使用 3.12.12)
- **Type Checking**: mypy (strict mode)
- **Testing**: pytest + pytest-asyncio
- **Async Runtime**: asyncio
- **Data Validation**: Pydantic
- **Configuration**: YAML + pydantic-settings
- **Logging**: structlog (structured logging)
- **Container Runtime**: Docker (for sandbox execution)

### Key Dependencies

```
langchain-openai
langchain-core
pytest
pytest-asyncio
# Optional: mcp (Model Context Protocol SDK)
```

## Project Structure

```
dare_framework/           # 框架核心实现
├── agent/                # Agent 域：编排策略（多实现）
│   ├── kernel.py         # IAgent 接口（最小运行面）
│   ├── interfaces.py     # IAgentOrchestration 等可插拔接口
│   ├── types.py          # Agent 相关类型
│   └── _internal/        # 默认实现（SimpleChatAgent, FiveLayerAgent）
├── context/              # 上下文工程域
│   ├── kernel.py         # IContext / IRetrievalContext 接口
│   ├── types.py          # Message, Budget, AssembledContext
│   └── _internal/        # Context 默认实现
├── tool/                 # 能力模型 + 系统调用边界
│   ├── kernel.py         # IToolGateway / IToolManager / IExecutionControl
│   ├── interfaces.py     # ITool / IToolProvider / IProtocolAdapter
│   ├── types.py          # CapabilityDescriptor, ToolResult
│   └── _internal/        # ToolManager, 内置工具, MCP 适配
├── plan/                 # 任务、计划、结果
│   ├── kernel.py         # 核心类型（Task, RunResult, Envelope）
│   ├── interfaces.py     # IPlanner / IValidator / IRemediator
│   └── _internal/        # CompositeValidator 等实现
├── model/                # LLM 调用适配
│   ├── kernel.py         # IModelAdapter 接口
│   ├── types.py          # ModelInput, ModelResponse, Prompt
│   └── _internal/        # OpenAI 适配器, Prompt 存储
├── security/             # Trust + Policy + Sandbox
│   ├── kernel.py         # ISecurityBoundary 接口
│   └── types.py          # 安全相关类型
├── event/                # 审计与重放
│   ├── kernel.py         # IEventLog 接口（WORM）
│   └── types.py          # Event 类型
├── memory/               # 记忆（STM/LTM）
│   ├── kernel.py         # IShortTermMemory / ILongTermMemory
│   └── _internal/        # InMemorySTM 实现
├── knowledge/            # 知识检索
│   ├── kernel.py         # IKnowledge 接口
│   └── _internal/        # VectorKnowledge 实现
├── config/               # 配置管理
│   ├── kernel.py         # IConfigProvider
│   ├── types.py          # Config 模型
│   └── _internal/        # FileConfigProvider
├── hook/                 # 生命周期扩展点
│   ├── kernel.py         # IHook / IExtensionPoint
│   └── _internal/        # CompositeExtensionPoint
├── builder/              # Layer 3: 开发者 API（确定性组装）
│   └── builder.py        # Builder / SimpleChatAgentBuilder / FiveLayerAgentBuilder
├── infra/                # 基础设施
│   └── component.py      # ComponentType 等共享组件类型
└── events/               # 事件总线
    ├── base.py
    └── event_bus.py

openspec/                 # OpenSpec 变更管理
├── project.md            # 项目上下文、技术栈、架构总览
├── config.yaml           # OpenSpec 配置
├── specs/                # 规范定义
│   └── */spec.md
└── changes/              # 变更提案
    └── archive/          # 已归档变更

doc/                      # 文档
├── design/               # 架构设计文档
│   ├── Architecture.md   # 最终架构设计（权威）
│   ├── Interfaces.md     # 权威接口清单
│   ├── DARE_alignment.md # 对齐清单
│   ├── DARE_evidence.yaml # 证据索引
│   └── archive/          # 历史归档
├── guides/               # 开发指南
│   ├── Development_Constraints.md
│   └── Engineering_Practice_Guide_Sandbox_and_WORM.md
├── appendix/             # 附录
└── README.md             # 文档导航

examples/                 # 示例实现
├── basic-chat/           # 简单聊天 Agent
├── coding-agent/         # 代码生成 Agent
├── five-layer-coding-agent/  # 五层循环完整示例
└── tool-management/      # 工具管理示例

tests/                    # 测试
├── unit/                 # 单元测试
├── integration/          # 集成测试
└── conftest.py           # pytest 配置
```

## Architecture

### 分层架构

```
Layer 3: Developer API（确定性组装）
  └── Builder / AgentBuilder / FiveLayerAgentBuilder

Layer 2: Pluggable Components（可插拔组件）
  └── Planner / Validator / Remediator / Model / Tools / Memory / Knowledge

Layer 1: Protocol Adapters（协议适配器）
  └── MCP / A2A / A2UI

Layer 0: Kernel 控制面（稳定边界）
  └── IContext / IToolGateway / ISecurityBoundary / IExecutionControl / IEventLog
```

### 五层循环编排

```
Session Loop    → 跨 context window 持久化
Milestone Loop  → Observe → Plan → Validate → Execute → Verify → Remediate
Plan Loop       → 生成有效计划，失败不外泄
Execute Loop    → LLM 驱动执行
Tool Loop       → Gather → Act → Check → Update (in WorkUnit)
```

### 信任边界

```
可信数据源（Ground Truth）           不可信数据源（需验证）
─────────────────────────           ─────────────────────────
• Tool Registry 元数据               • LLM 生成的 Plan
• Policy Engine 规则                 • LLM 填写的 risk_level
• Event Log 历史记录                 • LLM 声称的 coverage
• External Validator 结果            • LLM 生成的 evidence
• Human Approval 签名                • 用户输入（需消毒）
```

## Build and Test Commands

### Setup Environment

```bash
# 创建虚拟环境（使用 Python 3.12）
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### Run Tests

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_five_layer_agent.py

# 带覆盖率报告
pytest --cov=dare_framework --cov-report=html
```

### Code Quality Checks

```bash
# 代码格式化 (Black, line-length: 100)
black dare_framework/ tests/ examples/

# 代码检查
ruff check dare_framework/ tests/ examples/

# 类型检查 (strict mode)
mypy --strict dare_framework/

# 一键检查全部
black --check dare_framework/ tests/ && ruff check dare_framework/ tests/ && mypy --strict dare_framework/
```

### Run Examples

```bash
# 基础聊天示例
python examples/basic-chat/chat_simple.py

# 五层 Agent 示例（需配置 API Key）
export api_sk="your-api-key"
python examples/five-layer-coding-agent/interactive_cli.py
```

## Code Style Guidelines

### 命名规范

```python
class ToolRegistry:        # Classes: PascalCase
    _tools: dict           # Private: _prefix

def validate_step():       # Functions: snake_case
    pass

TRUSTED_SOURCES = [...]    # Constants: UPPER_SNAKE_CASE
```

### 类型注解

所有函数必须有完整的类型注解：

```python
async def invoke(
    self,
    tool_name: str,
    input: dict[str, Any],
    context: ExecutionContext,
) -> ToolResult:
    ...
```

### Docstrings

使用 Google 风格 docstring：

```python
def validate_plan(
    self,
    plan: ProposedPlan,
    context: AssembledContext,
) -> ValidatedPlan:
    """Validate a proposed plan.

    Args:
        plan: The plan proposed by the planner.
        context: Current assembled context.

    Returns:
        Validated plan with derived security fields.

    Raises:
        ValidationError: If plan is invalid.
    """
    ...
```

### Domain Package 结构约定

每个 domain 必须遵循：

```
dare_framework/<domain>/
  types.py          # 对外模型/枚举（相对稳定）
  kernel.py         # 该域最核心稳定接口（Kernel contract）
  interfaces.py     # 可插拔接口位、跨域组合接口位（可选）
  __init__.py       # export facade
  _internal/        # 默认实现（不稳定；不作为公共 API）
```

依赖规则：
- `types.py` 不依赖 `interfaces.py/_internal/`
- `kernel.py` 尽量只依赖 `types.py`
- `interfaces.py` 可依赖其他域 `kernel.py` 表达组合

## Testing Instructions

### 测试层次

1. **Unit Tests** (`tests/unit/`)
   - 每个模块的独立测试
   - Mock 所有外部依赖
   - 覆盖率目标: 90%+

2. **Integration Tests** (`tests/integration/`)
   - 组件间交互测试
   - 使用真实的 EventLog（本地文件）
   - 使用 Mock 的模型适配器

3. **E2E Tests** (`examples/five-layer-coding-agent/tests/`)
   - 完整的任务执行流程
   - 验证五层循环正确性

### 测试命名规范

```python
def test_trust_boundary_derives_risk_level_from_registry():
    """TrustBoundary 应该从 Registry 派生 risk_level，忽略 LLM 填写的"""
    ...

def test_tool_runtime_rejects_unknown_tool():
    """ToolGateway 应该拒绝未注册的工具"""
    ...
```

### 测试驱动开发要求

- **功能即测试**: 业务逻辑、接口、Bug 修复都必须有对应测试；缺测试的变更视为不完成
- **错误分支**: 对错误分支写回归测试
- **异步路径**: 使用 `pytest-asyncio`
- **隔离依赖**: 避免对外部网络/时钟的非隔离依赖（用 fixture/mocks）

## Security Considerations

### 核心安全规则

1. **不绕过 ToolGateway** - 所有工具调用必须通过 `IToolGateway.invoke()`
2. **高风险工具需要审批** - `requires_approval: true`
3. **LLM 输出永不可信** - 安全关键字段必须从可信源派生
4. **Event Log 只追加** - 没有 update/delete 方法

### 工具风险级别

| 级别 | 名称 | 含义 | 示例 |
|-----|-----|-----|-----|
| 1 | READ_ONLY | 只读，无副作用 | read_file, list_dir |
| 2 | IDEMPOTENT_WRITE | 幂等写入，可安全重试 | write_file, update_config |
| 3 | NON_IDEMPOTENT_EFFECT | 非幂等，需审批 | send_email, execute_command |
| 4 | COMPENSATABLE | 可补偿，有回滚能力 | create_pr (可 close) |

### 五个可验证闭环

每个安全机制都必须满足：
```
输入是什么 → 不可变事实是什么 → 系统强制在哪里 → 证据落在哪里 → 如何复验
```

1. **WORM 一致性** - Event 写入后不可修改
2. **Sandbox 强度** - seccomp/网络隔离
3. **Coverage 确定性** - 集合运算 `requires ⊆ produces`
4. **Context 注入隔离** - 不可信内容有边界标记
5. **Token 权限绑定** - 令牌绑定 (agent_id, task_id)

### 敏感数据处理

```python
# ❌ 错误：敏感数据进入日志
logger.info(f"Processing user {user.email} with password {user.password}")

# ✅ 正确：令牌化
logger.info(f"Processing user {tokenize(user.email)}")
```

## OpenSpec Workflow

所有重大变更必须通过 OpenSpec：

| 变更类型 | 需要 OpenSpec? | 说明 |
|---------|---------------|------|
| 新增核心接口 | 是 | 七个不可变接口的任何修改 |
| 新增组件 | 是 | 添加新的核心组件 |
| 架构调整 | 是 | 三层循环的任何修改 |
| 新增工具 | 视情况 | 高风险工具需要 |
| Bug 修复 | 否 | 直接修复并提交 |
| 重构（不改接口） | 否 | 确保测试通过 |
| 文档更新 | 否 | 直接提交 |

### 工作流程

1. **创建 Proposal**: 运行 `/openspec:proposal`
2. **等待评审**: 人类或其他 Agent 评审
3. **实现代码**: 评审通过后运行 `/openspec:apply`
4. **归档**: 部署后运行 `/openspec:archive`

## Development Constraints

### 总则

- 先看架构：不得破坏五层循环编排骨架、系统调用边界与核心接口契约
- 重大能力/接口变更走 OpenSpec
- 状态外化：所有进度、决策、证据写入文件/EventLog，避免依赖模型"记忆"
- 最小必要变更：新增功能时优先扩展现有组件/接口，避免跨层耦合

### 代码审查清单

在提交代码前，确保：

- [ ] 架构契约未破坏，信任边界与风险级别保持正确
- [ ] 所有函数有类型注解
- [ ] 所有公开方法有 docstring
- [ ] 所有测试通过 (`pytest`)
- [ ] 没有类型错误 (`mypy --strict`)
- [ ] 代码格式正确 (`black --check`)
- [ ] 没有 lint 错误 (`ruff`)
- [ ] 信任边界正确处理
- [ ] 敏感数据已令牌化
- [ ] EventLog 记录关键操作

### Commit 约定

使用 [Conventional Commits](https://www.conventionalcommits.org):

```
feat(tool-runtime): add approval checking for high-risk tools
feat(tool-gateway): enforce envelope allow-listing
fix(event-log): ensure hash chain continuity
refactor(validators): extract common validation logic
docs(readme): add architecture diagram
test(coverage): add deterministic coverage validator tests
```

## Key References

| 文档 | 用途 |
|-----|-----|
| `openspec/project.md` | 项目上下文、技术栈、架构总览 |
| `doc/design/Architecture.md` | 最终架构设计（权威） |
| `doc/design/Interfaces.md` | 权威接口清单 |
| `CONTRIBUTING_AI.md` | AI Agent 协作规则 |
| `doc/guides/Development_Constraints.md` | 开发约束清单 |
| `CLAUDE.md` | 快速参考卡片 |

## Additional Constraints

- When writing code, add necessary comments to clarify non-obvious logic or intent.
- When creating a commit, include a detailed commit message (summary + body with key changes and rationale).
