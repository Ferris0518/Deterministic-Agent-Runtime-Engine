# 08-hook-governance

基于真实 LLM（OpenRouter）的 Hook 治理 CLI 示例。

这个示例参考 `05` 的交互方式，但聚焦 Hook 本身，目标是让你在终端里直观看到 hook 生效：

1. `BEFORE_MODEL`：对 `ModelInput` 做 patch（自动给首条用户消息加 `[hook patched]` 前缀）
2. `BEFORE_MODEL`：当提示词包含 `#hook_block_model` 时直接 `BLOCK`
3. `BEFORE_TOOL`：拦截 `write_file` 工具调用并返回 `BLOCK`

## 运行

```bash
cd examples/08-hook-governance
export OPENROUTER_API_KEY="your-api-key"
# 可选
export OPENROUTER_MODEL="z-ai/glm-4.7"
export OPENROUTER_MAX_TOKENS="2048"
export OPENROUTER_TIMEOUT="60"
python main.py
```

也可以直接运行：

```bash
python cli.py --workspace ./workspace
```

说明：默认 `--workspace` 是你启动命令时的当前目录（`Path.cwd()`）。
如果你在仓库根目录启动，本仓库根下没有 `README.md`，请读取 `docs/README.md`。

## CLI 命令

- `/help`：查看帮助
- `/stats`：查看 Hook 统计（phase 次数、patch 次数、block 次数）
- `/quit`：退出

## 怎么验证 Hook 生效

1. 输入普通问题（例如：`请总结当前目录项目`）  
   你会在终端看到：`[HOOK] BEFORE_MODEL -> PATCH model_input`
2. 输入包含 `#hook_block_model` 的任务  
   例如：`#hook_block_model 请直接回答 hi`  
   你会看到：`[HOOK] BEFORE_MODEL -> BLOCK ...`
3. 输入让模型写文件的任务  
   例如：`在 workspace 下创建 demo.txt，内容是 hello`  
   若模型选择 `write_file`，会看到：`[HOOK] BEFORE_TOOL -> BLOCK write_file`
4. 输入要求读取文件的任务  
   例如：`请必须使用 read_file 工具读取当前目录 README.md，然后总结`  
   若模型触发工具调用，会看到：`[HOOK] BEFORE_TOOL -> ALLOW read_file`

## 文件结构

```text
08-hook-governance/
├── cli.py
├── main.py
└── README.md
```
