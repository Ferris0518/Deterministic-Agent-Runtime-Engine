"""
Simple Coding Agent Example

这个文件展示如何使用 DARE Framework 构建一个 Coding Agent。
通过这个示例验证框架的接口设计是否合理。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from typing import Iterable
from uuid import uuid4

from dare_framework import AgentBuilder
from dare_framework.components.interfaces import IModelAdapter
from dare_framework.core.models import GenerateOptions, Message, ModelResponse, Task, ToolCall, ToolDefinition

from tools import ReadFileTool, WriteFileTool, SearchCodeTool, RunTestsTool
from skills import FixBugSkill


class ScriptedModelAdapter(IModelAdapter):
    """Returns scripted tool calls sequentially, then declares done."""

    def __init__(self, tool_calls: Iterable[ToolCall]) -> None:
        self._tool_calls = list(tool_calls)
        self._index = 0

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        if self._index < len(self._tool_calls):
            call = self._tool_calls[self._index]
            self._index += 1
            return ModelResponse(content=f"calling {call.name}", tool_calls=[call])
        return ModelResponse(content="done", tool_calls=[])

    async def generate_structured(self, messages: list[Message], output_schema: type) -> object:
        return output_schema()


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
        workspace: str = ".",
        mock_mode: bool = True,
        tool_calls: Iterable[ToolCall] | None = None,
        model_adapter: IModelAdapter | None = None,
        plan_generator=None,
    ) -> None:
        builder = AgentBuilder("coding-agent").with_tools(
            ReadFileTool(workspace=workspace),
            WriteFileTool(workspace=workspace),
            SearchCodeTool(workspace=workspace),
            RunTestsTool(),
        ).with_skills(FixBugSkill())

        if mock_mode:
            default_calls = tool_calls or [
                ToolCall(id=f"call_{uuid4().hex}", name="read_file", input={"path": "README.md"})
            ]
            builder.with_model(ScriptedModelAdapter(default_calls))
        else:
            if model_adapter is None or plan_generator is None:
                raise ValueError("model_adapter and plan_generator are required when mock_mode=False")
            builder.with_model(model_adapter)
            builder.with_plan_generator(plan_generator)

        self._agent = builder.build()

    @classmethod
    def from_config(cls, config_path: str) -> "CodingAgent":
        """
        从配置文件创建 Agent

        验证：配置驱动是否方便？
        """
        # config = yaml.safe_load(open(config_path))
        # return cls(**config)
        raise NotImplementedError

    async def run(self, task: str):
        return await self._agent.run(Task(description=task), None)


async def main() -> None:
    agent = CodingAgent(
        workspace=".",
        mock_mode=True,
    )

    result = await agent.run(task="读取 README.md 并解释内容")
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
