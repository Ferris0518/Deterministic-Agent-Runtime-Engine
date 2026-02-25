"""Example 10: ReactAgent 代码侦查 - 对 agentscope/a2a 进行代码分析。

使用 ReactAgent 调用 read_file、search_code、search_file 等工具，
对指定目录进行代码侦查，分析模块结构、依赖关系和关键实现。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.agent import BaseAgent
from dare_framework.config import Config
from dare_framework.model import OpenRouterModelAdapter
from dare_framework.tool._internal.tools import (
    ReadFileTool,
    SearchCodeTool,
    SearchFileTool,
)

# 侦查目标：agentscope a2a 模块
TARGET_PATH = "D:\\Agent\\darev0.1\\Deterministic-Agent-Runtime-Engine\\agentscope\\src\\agentscope\\a2a"
DEFAULT_TASK = f"""请对以下目录进行代码侦查：

路径：{TARGET_PATH}

请完成以下分析：
1. 列出该目录下的所有 Python 文件及其作用
2. 分析模块的导出接口（__all__）和主要类/函数
3. 梳理模块间的依赖关系
4. 总结该模块的核心功能和设计意图

最后给出结构化报告。"""


async def main() -> None:
    """运行 ReactAgent 对 a2a 进行代码侦查。"""
    api_key = os.getenv("OPENROUTER_API_KEY","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")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        sys.exit(1)

    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
    max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))

    # 工作区设为项目根，以便访问 agentscope 目录
    workspace = PROJECT_ROOT
    if not (workspace / TARGET_PATH.replace("/", os.sep)).exists():
        print(f"Warning: Target path {TARGET_PATH} not found under {workspace}")
        print("Ensure agentscope submodule or directory exists.")

    model_adapter = OpenRouterModelAdapter(
        model=model_name,
        api_key=api_key,
        extra={"max_tokens": max_tokens},
    )

    agent_config = Config(
        workspace_dir=str(workspace),
        user_dir=str(Path.home()),
    )

    # 仅使用只读工具，适合代码侦查场景
    agent = await (
        BaseAgent.react_agent_builder("code-recon-agent")
        .with_model(model_adapter)
        .with_config(agent_config)
        .add_tools(ReadFileTool(), SearchCodeTool(), SearchFileTool())
        .build()
    )

    print(f"ReactAgent 代码侦查 (model: {model_name})")
    print(f"目标: {TARGET_PATH}")
    print("-" * 50)

    result = await agent(DEFAULT_TASK)

    print("\n" + "=" * 50)
    print("侦查报告:")
    print("=" * 50)
    print(result.output_text or str(result.output))
    if result.errors:
        print("\nErrors:", result.errors)


if __name__ == "__main__":
    asyncio.run(main())
