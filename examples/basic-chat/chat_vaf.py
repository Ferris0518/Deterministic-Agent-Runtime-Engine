"""Basic chat example using VAF (Versatile Agent Framework).

Demonstrates the simplified VAF architecture:
- 8 modules instead of 10
- Built-in hooks in BaseAgent
- Simplified types (Task, Step, Plan, RunResult)
- LoopAgent for multi-step execution
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path for local development
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Clean imports from VAF
from vaf import LoopAgent
from vaf.model import OpenAIModelAdapter
from vaf.tool import RunCommandTool

# Configuration - fill in your values
MODEL = "qwen-plus"
API_KEY = ""
ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# httpx does not expose allow_env_proxies; set trust_env=False to bypass proxies
HTTP_CLIENT_OPTIONS = {"trust_env": False, "proxy": None}
LOG_LEVEL = os.getenv("CHAT_LOG_LEVEL", "INFO").upper()

logger = logging.getLogger("chat-vaf")


def _preview(text: str, limit: int = 200) -> str:
    """Truncate text for logging preview."""
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...<truncated>"


async def main() -> None:
    """Main entry point for the VAF chat agent."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger.info(
        "boot VAF chat agent",
        extra={
            "model": MODEL,
            "endpoint": ENDPOINT,
            "api_key_set": bool(API_KEY),
        },
    )

    # Build model adapter
    model_adapter = OpenAIModelAdapter(
        model=MODEL,
        api_key=API_KEY,
        endpoint=ENDPOINT,
        http_client_options=HTTP_CLIENT_OPTIONS,
    )

    # Create agent using VAF's LoopAgent
    agent = LoopAgent(
        name="chat-vaf",
        model=model_adapter,
        tools=[RunCommandTool()],
        system_prompt="你是一个乐于助人的AI助手。可以使用工具执行命令来帮助用户完成任务。",
        max_iterations=10,
    )

    print("VAF Chat Agent 已启动。输入消息开始对话，输入 /quit 退出。")
    print("-" * 50)

    # Interactive chat loop
    while True:
        try:
            raw = input("You: ")
        except EOFError:
            break
        prompt = raw.strip()
        if not prompt:
            continue
        if prompt == "/quit":
            print("再见！")
            break

        logger.info("running prompt", extra={"prompt": _preview(prompt)})
        try:
            result = await agent.run(prompt)
        except Exception as exc:
            logger.exception("agent run failed")
            print(f"[错误] 运行失败: {exc}", file=sys.stderr, flush=True)
            continue

        if not result.success:
            logger.warning("agent returned failure", extra={"errors": result.errors})
            print(f"[错误] {result.errors}", file=sys.stderr, flush=True)
            continue

        # Extract content from result
        content = result.output
        if content is None:
            print("AI: (无输出)", flush=True)
            continue

        # Handle different output types
        if isinstance(content, str):
            print(f"AI: {content}", flush=True)
        elif isinstance(content, list):
            # Tool results
            for item in content:
                if hasattr(item, "output"):
                    print(f"AI: {item.output}", flush=True)
                else:
                    print(f"AI: {item}", flush=True)
        else:
            print(f"AI: {content}", flush=True)

        logger.info("assistant reply", extra={"content": _preview(str(content))})


if __name__ == "__main__":
    asyncio.run(main())
