# 10-react-agent-code-recon

对标 **Claude Code** 的项目级 AI 编程助手。针对一个目标工程，支持深度理解、修改代码、执行命令。

## 功能

- **深度理解**：探索代码结构、回答代码问题
- **修改代码**：添加功能、修复 bug、重构
- **执行**：运行测试、构建、命令

## 架构

- **Plan Agent**：编排大颗粒步骤，委托 sub-agent
- **sub_agent_recon**：只读（read_file, search_code, search_file）
- **sub_agent_coder**：可写（read_file, write_file, search_code, edit_line）
- **sub_agent_runner**：可执行（run_command, read_file）

## 运行

```bash
cd examples/10-react-agent-code-recon
export OPENROUTER_API_KEY="your-api-key"
# 可选
export OPENROUTER_MODEL="openai/gpt-oss-120b"
export OPENROUTER_MAX_TOKENS="4096"

# 指定目标工程
python plan_claude_code.py                          # 目标 = 当前目录
python plan_claude_code.py .                        # 同上
python plan_claude_code.py D:/Agent/realesrgan/Real-ESRGAN
```

## 对话式交互

进入 `task>` 提示符后，直接输入任务或使用 `/help`、`/quit`。

**任务类型**（自然语言）：理解项目、回答问题、修改代码、运行测试

## 文件结构

```
10-react-agent-code-recon/
├── main.py              # 单 React 代码侦查（不修改）
├── plan_claude_code.py  # 对标 Claude Code（对话式）
└── README.md
```
