from __future__ import annotations

import asyncio

from dare_framework.components.model_adapters.openai import OpenAIModelAdapter
from dare_framework.components.tools.run_command import RunCommandTool
from dare_framework.composition.builder import AgentBuilder
from dare_framework.core.models.plan import Task


async def main() -> None:
    prompt = input("You: ").strip()
    if not prompt:
        return

    builder = AgentBuilder("basic-chat")
    builder.with_model(OpenAIModelAdapter())
    builder.with_tools(RunCommandTool())
    agent = builder.build()

    result = await agent.run(Task(description=prompt), None)
    if not result.output:
        print("No output returned.")
        return
    last = result.output[-1]
    content = getattr(last, "output", {}).get("content", "")
    print(content)


if __name__ == "__main__":
    asyncio.run(main())
