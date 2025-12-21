# Project Context

## Purpose

**DARE Framework** (Deterministic Agent Runtime Engine) 是一个工业级 AI Agent 执行框架，专为需要高安全性、可审计性和多 Agent 协作的场景设计。

### 核心目标

1. **银行/金融场景** - 强审计、合规、人在回路（Human-in-the-loop）
2. **代码生成场景** - 容错、迭代、外部验证
3. **多 Agent 协作** - 任务租约、冲突处理、统一状态

### 设计理念

| 理念 | 含义 |
|-----|-----|
| **状态外化** | 所有状态存 EventLog/DB，不依赖模型记忆 |
| **LLM 不可信** | Plan 产出只是"意图"，安全关键字段从可信源派生 |
| **外部可验证** | "完成"由外部验证器判定，不信任模型说"done" |
| **增量执行** | 每步做完提交，留清晰交接物 |
| **可审计** | 每个决策有结构化记录 + 证据链 |

## Tech Stack

- **Primary Language**: Python 3.11+
- **Type Checking**: mypy (strict mode)
- **Testing**: pytest + pytest-asyncio
- **Async Runtime**: asyncio
- **Data Validation**: Pydantic v2
- **Configuration**: YAML + pydantic-settings
- **Logging**: structlog (structured logging)
- **Container Runtime**: Docker (for sandbox execution)

### Optional/Future
- **Event Storage**: PostgreSQL / S3 (for WORM storage)
- **Message Queue**: Redis Streams / Kafka (for distributed mode)
- **Observability**: OpenTelemetry

## Project Conventions

### Code Style

- **Formatter**: Black (line-length: 100)
- **Linter**: Ruff
- **Import Sorting**: isort (compatible with Black)
- **Docstrings**: Google style

```python
# Naming conventions
class ToolRegistry:        # Classes: PascalCase
    _tools: dict           # Private: _prefix

def validate_step():       # Functions: snake_case
    pass

TRUSTED_SOURCES = [...]    # Constants: UPPER_SNAKE_CASE
```

### Type Hints

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

### Architecture Patterns

#### 三层循环架构

```
┌─────────────────────────────────────────────────────────────────┐
│  Session Loop (跨 Context Window)                                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Milestone Loop                                          │    │
│  │  Observe → Plan → Validate → Execute → Verify            │    │
│  │                      ↓                   ↑               │    │
│  │  ┌─────────────────────────────────────────┐            │    │
│  │  │  Tool Loop (in WorkUnit)                 │            │    │
│  │  │  Gather → Act → Check → Update           │            │    │
│  │  └─────────────────────────────────────────┘            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

**Session Loop**: 跨 context window 保持状态，通过 EventLog 和 Checkpoint 实现长任务持久化

**Milestone Loop**: 六步编排
- Observe: 收集任务输入 + 当前状态快照
- Plan: LLM 生成计划（不可信）
- Validate: TrustBoundary + Coverage + Policy 验证
- Execute: 按步骤执行（所有工具调用走 ToolRuntime）
- Verify: 按 Expectation.verification_spec 执行验收
- Remediate: 验证失败则触发补救循环

**Tool Loop**: WorkUnit 内部高效迭代，Envelope 持有 DonePredicate

#### 核心组件

```
agent_framework/
├── core/                  # 核心框架代码
│   ├── runtime.py         # AgentRuntime 主循环
│   ├── state.py           # RunState 状态模型
│   ├── events.py          # 事件类型定义
│   └── errors.py          # 错误分类
├── components/            # 核心组件
│   ├── model_adapter.py   # 模型适配器
│   ├── tool_registry.py   # 工具注册表
│   ├── tool_runtime.py    # 工具执行运行时
│   ├── policy_engine.py   # 策略引擎
│   ├── context_assembler.py
│   ├── event_log.py       # 事件日志
│   └── evidence_factory.py
├── validators/            # 验证器
│   ├── trust_boundary.py
│   ├── coverage_validator.py
│   ├── input_sanitizer.py
│   └── done_validator.py
└── plugins/               # 可插拔扩展
    ├── tools/
    ├── skills/
    └── models/
```

#### 七个不可变接口

1. `IModelAdapter` - 模型适配器
2. `IToolRegistry` - 工具注册表
3. `IToolRuntime` - 工具执行运行时（唯一的工具调用入口）
4. `IPolicyEngine` - 策略引擎
5. `IEventLog` - 事件日志（append-only）
6. `IContextAssembler` - 上下文装配器
7. `IVerifier` - 验证器

### Testing Strategy

#### 测试层次

1. **Unit Tests** (`tests/unit/`)
   - 每个模块的独立测试
   - Mock 所有外部依赖
   - 覆盖率目标: 90%+

2. **Integration Tests** (`tests/integration/`)
   - 组件间交互测试
   - 使用真实的 EventLog（本地文件）
   - 使用 Mock 的模型适配器

3. **E2E Tests** (`tests/e2e/`)
   - 完整的任务执行流程
   - 验证六步编排正确性

#### 测试命名

```python
def test_trust_boundary_derives_risk_level_from_registry():
    """TrustBoundary 应该从 Registry 派生 risk_level，忽略 LLM 填写的"""
    ...

def test_tool_runtime_rejects_unknown_tool():
    """ToolRuntime 应该拒绝未注册的工具"""
    ...
```

### Git Workflow

#### 分支策略

- `main` - 稳定分支，只接受 PR
- `develop` - 开发分支
- `feature/*` - 功能分支
- `fix/*` - 修复分支
- `openspec/*` - OpenSpec change proposal 分支

#### Commit 约定

使用 [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(tool-runtime): add approval checking for high-risk tools
fix(event-log): ensure hash chain continuity
refactor(validators): extract common validation logic
docs(readme): add architecture diagram
test(coverage): add deterministic coverage validator tests
```

#### OpenSpec 工作流

所有重大变更必须通过 OpenSpec:

1. 创建 proposal: `/openspec:proposal`
2. 评审通过后实现: `/openspec:apply`
3. 部署后归档: `/openspec:archive`

详见 `openspec/AGENTS.md`

## Domain Context

### 信任边界

```
┌─────────────────────────────────────────────────────────────────┐
│                      Trust Boundary 信任边界                     │
├─────────────────────────────────────────────────────────────────┤
│  可信数据源（Ground Truth）           不可信数据源（需验证）       │
│  ─────────────────────────           ─────────────────────────  │
│  • Tool Registry 元数据               • LLM 生成的 Plan          │
│  • Policy Engine 规则                 • LLM 填写的 risk_level    │
│  • Event Log 历史记录                 • LLM 声称的 coverage      │
│  • External Validator 结果            • LLM 生成的 evidence      │
│  • Human Approval 签名                • 用户输入（需消毒）        │
└─────────────────────────────────────────────────────────────────┘
```

### 工具风险级别

| 级别 | 名称 | 含义 | 示例 |
|-----|-----|-----|-----|
| 1 | READ_ONLY | 只读，无副作用 | read_file, list_dir |
| 2 | IDEMPOTENT_WRITE | 幂等写入，可安全重试 | write_file, update_config |
| 3 | NON_IDEMPOTENT_EFFECT | 非幂等，需审批 | send_email, execute_command |
| 4 | COMPENSATABLE | 可补偿，有回滚能力 | create_pr (可 close) |

### 五个可验证闭环

每个安全机制都必须满足闭环：

```
输入是什么 → 不可变事实是什么 → 系统强制在哪里 → 证据落在哪里 → 如何复验
```

1. **WORM 一致性** - Event 写入后不可修改
2. **Sandbox 强度** - seccomp/网络隔离
3. **Coverage 确定性** - 集合运算 `requires ⊆ produces`
4. **Context 注入隔离** - 不可信内容有边界标记
5. **Token 权限绑定** - 令牌绑定 (agent_id, task_id)

## Important Constraints

### 安全约束

- **所有工具调用必须经过 ToolRuntime** - 不允许绕过
- **高风险工具需要审批** - `requires_approval: true`
- **LLM 输出永不可信** - 安全关键字段必须从可信源派生
- **Event Log 只追加** - 没有 update/delete 方法

### 性能约束

- **Tool 执行超时**: 默认 30 秒，可配置
- **Plan 生成超时**: 60 秒
- **最大补救次数**: 3 次

### 合规约束

- **审计日志保留**: 7 年（金融场景）
- **敏感数据令牌化**: 不进入模型上下文
- **操作可追溯**: 每个操作有 trace_id

## External Dependencies

### LLM Providers

- Anthropic Claude (primary)
- OpenAI GPT (fallback)
- 其他兼容 OpenAI API 的模型

### 存储

- 本地文件系统 (MVP)
- PostgreSQL (生产)
- S3 with Object Lock (WORM 存储)

### 沙箱运行时

- Docker (代码执行隔离)
- seccomp (系统调用过滤)

## References

- [设计文档 v2.0-v2.4](/doc/design/)
- [框架骨架 v1](/doc/design/Agent_Framework_Skeleton_v1.md)
- [循环模型 v2.2](/doc/design/Agent_Framework_Loop_Model_v2.2_Final.md)
- [Anthropic Engineering 博客](/doc/design/anthropic-engineering.md)
