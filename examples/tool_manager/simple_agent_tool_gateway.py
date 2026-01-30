"""SimpleChatAgent tool gateway example using dare_framework (builder-based).

Demonstrates the tool runtime with:
- IToolGateway as the user-facing boundary (ToolManager implementation)
- IToolProvider for supplying tools to the gateway registry
- Trusted tool listings derived from the gateway registry
- Direct tool invocation via the gateway boundary
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path for local development.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dare_framework.builder import Builder  # noqa: E402
from dare_framework.config import build_config_provider  # noqa: E402
from dare_framework.infra.component import ComponentType  # noqa: E402
from dare_framework.model import IModelAdapter  # noqa: E402
from dare_framework.plan import Envelope  # noqa: E402
from dare_framework.tool import (  # noqa: E402
    EditLineTool,
    IToolGateway,
    IToolProvider,
    NativeToolProvider,
    NoOpTool,
    ReadFileTool,
    RunCommandTool,
    RunContextState,
    SearchCodeTool,
    ToolManager,
    WriteFileTool,
)


# Builder requires a model adapter even when this example only exercises tools.
class _NoopModelAdapter(IModelAdapter):
    @property
    def name(self) -> str:
        return "noop-model-adapter"

    @property
    def component_type(self) -> ComponentType:
        return ComponentType.MODEL_ADAPTER

    async def generate(self, prompt, *, options=None):  # type: ignore[override]
        raise RuntimeError("NoopModelAdapter is not intended for model generation.")


# Configuration
WORKSPACE_ROOT = os.getenv("TOOL_WORKSPACE_ROOT", ".")
READ_PATH = os.getenv("TOOL_READ_PATH", "examples/tool_manager/README.md")
LOG_LEVEL = os.getenv("TOOL_LOG_LEVEL", "INFO").upper()
REGISTRY_MODE = os.getenv("TOOL_REGISTRY_MODE", "provider").lower()

logger = logging.getLogger("simple-agent-tool-gateway")


def _build_tool_gateway(
    tools: list,
    run_context: RunContextState,
    registry_mode: str,
) -> IToolGateway:
    """Build a ToolManager and register tools via provider or direct calls."""
    manager = ToolManager(context_factory=run_context.build)
    if registry_mode == "provider":
        tool_provider: IToolProvider = NativeToolProvider(tools=tools)
        manager.register_provider(tool_provider)
    elif registry_mode == "direct":
        # Direct registration grants per-tool lifecycle control.
        for tool in tools:
            manager.register_tool(tool)
    else:
        raise ValueError(
            f"Unknown TOOL_REGISTRY_MODE '{registry_mode}'. Use 'provider' or 'direct'."
        )
    return manager


async def run_read_file(workspace_root: str, read_path: str, registry_mode: str):
    """Build the tool runtime and execute a read_file tool call."""
    # Tool settings are loaded from .dare/config.json via the config provider.
    config_provider = build_config_provider(workspace_dir=workspace_root)
    config = config_provider.current()
    run_context = RunContextState(config=config)

    tools = [
        ReadFileTool(),
        SearchCodeTool(),
        WriteFileTool(),
        EditLineTool(),
        RunCommandTool(),
        NoOpTool(),
    ]

    tool_gateway = _build_tool_gateway(tools, run_context, registry_mode)
    builder = (
        Builder.simple_chat_agent_builder("simple-agent-tool-gateway")
        .with_model(_NoopModelAdapter())
        .with_tool_gateway(tool_gateway)
        .with_config(config)
    )
    agent = builder.build()

    tool_defs = agent.context.listing_tools()
    capabilities = await tool_gateway.list_capabilities()
    read_tool_id = next(cap.id for cap in capabilities if cap.name == "read_file")
    result = await tool_gateway.invoke(
        read_tool_id,
        {"path": read_path},
        envelope=Envelope(allowed_capability_ids=[read_tool_id]),
    )
    return tool_defs, result


async def main() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger.info(
        "boot simple-agent tool gateway example",
        extra={
            "workspace_root": WORKSPACE_ROOT,
            "read_path": READ_PATH,
            "registry_mode": REGISTRY_MODE,
        },
    )

    tool_defs, result = await run_read_file(WORKSPACE_ROOT, READ_PATH, REGISTRY_MODE)
    tool_names = [tool["function"]["name"] for tool in tool_defs]
    logger.info("tool defs ready", extra={"tool_names": tool_names})
    print(f"Tool defs: {tool_names}")

    logger.info("read_file completed", extra={"success": result.success})
    print(f"Read success: {result.success}")
    print(f"Read path: {result.output.get('path')}")


if __name__ == "__main__":
    asyncio.run(main())
