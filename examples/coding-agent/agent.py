"""
Simple Coding Agent Example

这个文件展示如何使用 DARE Framework 构建一个 Coding Agent。
通过这个示例验证框架的接口设计是否合理。
"""

from typing import Optional

# === 框架导入（验证：导入是否清晰？） ===
# from dare_framework import AgentBuilder, IAgent, Task, RunResult
# from dare_framework.models import ClaudeAdapter
# from dare_framework.memory import VectorMemory
# from dare_framework.hooks import LoggingHook

# === 本地工具导入 ===
from tools import ReadFileTool, WriteFileTool, SearchCodeTool, RunTestsTool
from skills import FixBugSkill


# === Agent 定义 ===

class CodingAgent:
    """
    Coding Agent 示例

    能力：
    - 读写代码文件
    - 搜索代码
    - 运行测试
    - 修复 Bug

    这个类展示了开发者如何组装一个 Agent。
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        workspace: str = ".",
        enable_memory: bool = True,
    ):
        """
        初始化 Agent

        Args:
            model: 使用的模型
            workspace: 工作目录
            enable_memory: 是否启用记忆
        """
        self.model = model
        self.workspace = workspace

        # 构建 Agent（验证：AgentBuilder 是否易用？）
        # self._agent = (
        #     AgentBuilder("coding-agent")
        #     .description("A coding assistant that can read, write, and test code")
        #
        #     # 注册工具（验证：添加工具是否简单？）
        #     .with_tools(
        #         ReadFileTool(workspace=workspace),
        #         WriteFileTool(workspace=workspace),
        #         SearchCodeTool(workspace=workspace),
        #         RunTestsTool(workspace=workspace),
        #     )
        #
        #     # 注册技能（验证：技能与工具的关系是否清晰？）
        #     .with_skill(FixBugSkill())
        #
        #     # 配置记忆（验证：记忆是否易于配置？）
        #     .with_memory(
        #         VectorMemory(
        #             embedder=OpenAIEmbedder(),
        #             storage=LocalStorage("./memory"),
        #         ) if enable_memory else None
        #     )
        #
        #     # 添加钩子（验证：钩子是否足够灵活？）
        #     .with_hook(LoggingHook(level="DEBUG"))
        #
        #     # 配置模型（验证：模型切换是否简单？）
        #     .with_model(ClaudeAdapter(model=model))
        #
        #     .build()
        # )

    @classmethod
    def from_config(cls, config_path: str) -> "CodingAgent":
        """
        从配置文件创建 Agent

        验证：配置驱动是否方便？
        """
        # config = yaml.safe_load(open(config_path))
        # return cls(**config)
        pass

    async def run(self, task: str) -> "RunResult":
        """
        执行任务

        Args:
            task: 任务描述

        Returns:
            RunResult: 执行结果

        验证：
        1. 任务描述转换为 Task 对象是否合理？
        2. 执行结果 RunResult 是否包含足够信息？
        """
        # return await self._agent.run(Task(description=task))
        pass

    async def run_with_expectations(
        self,
        task: str,
        expectations: list[str],
    ) -> "RunResult":
        """
        执行带有验收条件的任务

        验证：
        1. Expectation 的定义是否清晰？
        2. VerificationSpec 是否易于构建？
        """
        # return await self._agent.run(
        #     Task(
        #         description=task,
        #         expectations=[
        #             Expectation(
        #                 description=exp,
        #                 priority="MUST",
        #                 verification_spec=VerificationSpec(
        #                     type="test_pass",
        #                     config={}
        #                 )
        #             )
        #             for exp in expectations
        #         ]
        #     )
        # )
        pass


# === 使用示例 ===

async def main():
    """使用示例"""

    # 创建 Agent
    agent = CodingAgent(
        model="claude-sonnet-4-20250514",
        workspace="/path/to/project",
        enable_memory=True,
    )

    # 简单任务
    result = await agent.run(
        task="读取 src/main.py 并解释这段代码的功能"
    )

    # 带验收条件的任务
    result = await agent.run_with_expectations(
        task="修复 src/utils.py 中的类型错误",
        expectations=[
            "所有测试通过",
            "没有 mypy 错误",
        ]
    )

    print(f"Success: {result.success}")
    print(f"Output: {result.output}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
