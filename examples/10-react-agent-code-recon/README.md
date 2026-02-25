# 10-react-agent-code-recon

使用 **ReactAgent** 对指定代码目录进行代码侦查（Code Reconnaissance）。

## 功能

- 调用 `read_file`、`search_code`、`search_file` 等只读工具
- 对 `agentscope/src/agentscope/a2a` 进行结构化分析
- 输出：文件列表、导出接口、依赖关系、核心功能总结

## 运行

```bash
cd examples/10-react-agent-code-recon
export OPENROUTER_API_KEY="your-api-key"
# 可选
export OPENROUTER_MODEL="z-ai/glm-4.7"
export OPENROUTER_MAX_TOKENS="4096"
python main.py
```

## 前置条件

- 项目根目录下需存在 `agentscope` 子模块或目录
- 若 `agentscope` 为 git submodule，请先执行 `git submodule update --init`

## 代码要点

- 使用 `BaseAgent.react_agent_builder()` 构建 ReactAgent
- `workspace_dir` 设为项目根，以便工具访问 `agentscope` 路径
- 仅注册只读工具，适合代码侦查场景
- 单次执行，无交互式 CLI

## 文件结构

```
10-react-agent-code-recon/
├── main.py
└── README.md
```
