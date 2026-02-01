# 03-dare-coding-agent

使用 `DareAgentBuilder` 演示完整五层循环，并提供可演示的交互式 CLI。

## 快速开始

```bash
# 进入目录
cd examples/03-dare-coding-agent

# 配置环境（OpenRouter）
cp .env.example .env
# 编辑 .env 添加你的 OPENROUTER_API_KEY

# 运行交互式 CLI
python main.py
```

默认模型使用 `OPENROUTER_MODEL`，未设置时默认为 `z-ai/glm-4.7`。
若账号 credits 较少，建议设置 `OPENROUTER_MAX_TOKENS=2048`。
如需限制请求时间，可设置 `OPENROUTER_TIMEOUT=60`（秒）。

## CLI 用法

交互命令：
- `/mode plan`：计划预览模式（先生成计划，等待 /approve 执行）
- `/mode execute`：直接执行模式（ReAct）
- `/approve`：执行当前待审批计划
- `/reject`：取消当前计划
- `/status`：查看状态
- `/help`：帮助
- `/quit`：退出

### 演示脚本

一键演示（推荐给演示场景）：

```bash
python cli.py --demo demo_script.txt
# 或
python demo.py
```

## 架构

```
┌─────────────────────────────────────────────────────────────────┐
│  Session Loop (跨 Context Window)                                │
│  └─ Milestone Loop (Observe → Plan → Execute → Verify)           │
│     ├─ Plan Loop (生成证据型计划)                                 │
│     ├─ Execute Loop (LLM 驱动执行)                               │
│     └─ Tool Loop (工具调用)                                       │
└─────────────────────────────────────────────────────────────────┘
```

## 核心代码（简化）

```python
agent = (
    DareAgentBuilder("dare-coding-agent")
    .with_model(OpenRouterModelAdapter(...))
    .add_tools(ReadFileTool(), WriteFileTool(), SearchCodeTool(), RunCommandTool())
    .with_planner(DefaultPlanner(model))
    .add_validators(FileExistsValidator(workspace))
    .with_remediator(DefaultRemediator(model))
    .build()
)
```

## Skill 挂载

一个 agent 同时只支持一个 skill。框架支持：

- **Builder**：`.with_skill(path)` 设置初始 skill
- **Config**：`initial_skill_path` 设置初始 skill
- **运行时**：`agent.set_skill(skill)` / `agent.clear_skill()` 动态挂载、替换、删除

Skill prompt 在 context.assemble() 时作为单独一段注入，与 base prompt 解耦。

示例 CLI 通过 `--skill` 传入路径：

```bash
python cli.py --skill path/to/my_skill
```

Skill 目录结构（Agent Skills 格式）：

```
my_skill/
├── SKILL.md        # YAML frontmatter + markdown 正文
└── scripts/        # 可执行脚本
    ├── run_tool.py
    └── check.sh
```

## Prompt 管理说明

系统提示由框架 Prompt Store 管理（默认 `base.system`），并自动合并 skill 内容。
如需覆盖，使用 `.dare/_prompts.json` 配置。

## 工具命名规则

工具 `name` 是唯一主键（capability id）。自定义工具时必须保证名称唯一。

## 文件结构

```
04-dare-coding-agent-enhanced/
├── main.py
├── cli.py
├── demo.py
├── demo_script.txt
├── validators/
│   └── file_validator.py
├── workspace/
└── README.md
```
