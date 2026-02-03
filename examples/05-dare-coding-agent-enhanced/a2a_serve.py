"""Run the DARE coding agent as an A2A server (https://a2acn.com/).

Usage:
    pip install uvicorn starlette
    python a2a_serve.py [--port 8010] [--host 0.0.0.0]

Then:
    GET http://localhost:8010/.well-known/agent.json  -> AgentCard
    POST http://localhost:8010/  with JSON-RPC body:
        {"jsonrpc":"2.0","id":1,"method":"tasks/send","params":{"id":"t1","message":{"role":"user","parts":[{"type":"text","text":"Hello"}]}}}
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Project root for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.a2a.server import build_agent_card, create_a2a_app
from dare_framework.agent import DareAgentBuilder
from dare_framework.config import FileConfigProvider
from dare_framework.knowledge import InMemoryRawDataStorage, RawDataKnowledge
from dare_framework.model import OpenRouterModelAdapter
from dare_framework.plan import DefaultPlanner, DefaultRemediator
from dare_framework.tool import ReadFileTool, SearchCodeTool, RunCommandTool, WriteFileTool, RunContext


def _create_builder(workspace: Path, config, model_name: str, api_key: str, max_tokens: int, timeout_seconds: float) -> DareAgentBuilder:
    model = OpenRouterModelAdapter(
        model=model_name,
        api_key=api_key,
        extra={"max_tokens": max_tokens},
        http_client_options={"timeout": timeout_seconds},
    )
    storage = InMemoryRawDataStorage()
    knowledge = RawDataKnowledge(storage=storage)
    return (
        DareAgentBuilder("dare-coding-agent")
        .with_model(model)
        .with_knowledge(knowledge)
        .with_planner(DefaultPlanner())
        .with_remediator(DefaultRemediator())
        .with_config(config)
        .with_tools([
            ReadFileTool(root=workspace),
            WriteFileTool(root=workspace),
            SearchCodeTool(root=workspace),
            RunCommandTool(root=workspace),
            RunContext(root=workspace),
        ])
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="DARE A2A server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8010, help="Bind port")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    api_key = os.getenv("OPENROUTER_API_KEY") or ""
    if not api_key:
        print("OPENROUTER_API_KEY not set; set it or export for model calls.")
        sys.exit(1)

    example_dir = Path(__file__).parent
    config_provider = FileConfigProvider(workspace_dir=example_dir, user_dir=Path.home())
    config = config_provider.current()

    workspace = example_dir / "workspace"
    workspace.mkdir(exist_ok=True)
    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "2048"))
    timeout_seconds = float(os.getenv("OPENROUTER_TIMEOUT", "60"))

    builder = _create_builder(workspace, config, model_name, api_key, max_tokens, timeout_seconds)
    agent = await builder.build()

    base_url = f"http://{args.host}:{args.port}".replace("0.0.0.0", "localhost")
    card = build_agent_card(config, base_url, name="DARE Coding Agent", description="Coding agent with tools and skills")
    app = create_a2a_app(card, agent.run, workspace_dir=str(workspace))

    print(f"A2A server: {base_url}")
    print(f"  GET  /.well-known/agent.json  -> AgentCard")
    print(f"  POST /  -> JSON-RPC (tasks/send, tasks/get, tasks/cancel)")
    print("Press Ctrl+C to stop.")

    try:
        import uvicorn
        config_uvicorn = uvicorn.Config(app, host=args.host, port=args.port, log_level="info")
        server = uvicorn.Server(config_uvicorn)
        await server.serve()
    except ImportError:
        print("uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
