"""Runtime bootstrap for the client CLI."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from dare_framework.agent import DareAgentBuilder
from dare_framework.config import Config, FileConfigProvider
from dare_framework.model.default_model_adapter_manager import DefaultModelAdapterManager
from dare_framework.plan import DefaultPlanner, DefaultRemediator
from dare_framework.tool._internal.tools import ReadFileTool, RunCommandTool, SearchCodeTool, WriteFileTool
from dare_framework.transport import AgentChannel, DirectClientChannel


@dataclass(frozen=True)
class RuntimeOptions:
    """CLI-provided runtime overrides."""

    workspace_dir: Path
    user_dir: Path
    model: str | None = None
    adapter: str | None = None
    api_key: str | None = None
    endpoint: str | None = None
    max_tokens: int | None = None
    timeout_seconds: float | None = None
    mcp_paths: list[str] | None = None


@dataclass
class ClientRuntime:
    """Initialized runtime object shared by command handlers."""

    agent: Any
    channel: AgentChannel
    client_channel: DirectClientChannel
    config_provider: FileConfigProvider
    config: Config
    model: Any
    options: RuntimeOptions

    async def close(self) -> None:
        """Gracefully stop agent/channel lifecycle."""
        await self.agent.stop()

    async def reload_config(self) -> Config:
        """Reload file-backed config and re-apply CLI overrides."""
        self.config = apply_runtime_overrides(self.config_provider.reload(), self.options)
        return self.config


def load_effective_config(options: RuntimeOptions) -> tuple[FileConfigProvider, Config]:
    """Load file-backed config and apply CLI overrides without building runtime."""
    provider = FileConfigProvider(
        workspace_dir=options.workspace_dir,
        user_dir=options.user_dir,
    )
    config = apply_runtime_overrides(provider.current(), options)
    return provider, config


def _normalize_mcp_paths(paths: list[str], base_dir: Path) -> list[str]:
    normalized: list[str] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            # Keep config authoring friendly while runtime loading stays deterministic.
            p = (base_dir / p).resolve()
        normalized.append(str(p))
    return normalized


def _resolve_config_paths(config: Config, workspace_dir: Path) -> Config:
    if not config.mcp_paths:
        return config
    normalized = _normalize_mcp_paths(list(config.mcp_paths), workspace_dir)
    if normalized == list(config.mcp_paths):
        return config
    return replace(config, mcp_paths=normalized)


def apply_runtime_overrides(config: Config, options: RuntimeOptions) -> Config:
    """Apply CLI flags on top of file-backed Config."""
    effective = config
    effective = replace(
        effective,
        workspace_dir=str(options.workspace_dir),
        user_dir=str(options.user_dir),
    )
    effective = _resolve_config_paths(effective, options.workspace_dir)

    llm = effective.llm
    if options.model is not None:
        llm = replace(llm, model=options.model)
    if options.adapter is not None:
        llm = replace(llm, adapter=options.adapter)
    if options.api_key is not None:
        llm = replace(llm, api_key=options.api_key)
    if options.endpoint is not None:
        llm = replace(llm, endpoint=options.endpoint)
    if options.max_tokens is not None:
        llm = replace(llm, extra={**dict(llm.extra), "max_tokens": int(options.max_tokens)})
    effective = replace(effective, llm=llm)

    if options.mcp_paths:
        effective = replace(
            effective,
            mcp_paths=_normalize_mcp_paths(list(options.mcp_paths), options.workspace_dir),
        )
    return effective


async def bootstrap_runtime(options: RuntimeOptions) -> ClientRuntime:
    """Build and start the agent runtime for CLI usage."""
    provider, config = load_effective_config(options)
    model_manager = DefaultModelAdapterManager(config=config)
    model = model_manager.load_model_adapter(config=config)
    if model is None:
        raise RuntimeError("model adapter manager returned no model adapter")

    client_channel = DirectClientChannel()
    channel = AgentChannel.build(client_channel)
    builder = (
        DareAgentBuilder("dare-client-cli")
        .with_config(config)
        .with_config_provider(provider)
        .with_model(model)
        .with_agent_channel(channel)
        .add_tools(ReadFileTool(), WriteFileTool(), SearchCodeTool(), RunCommandTool())
        .with_planner(DefaultPlanner(model, verbose=False))
        .with_remediator(DefaultRemediator(model, verbose=False))
    )
    agent = await builder.build()
    await agent.start()
    return ClientRuntime(
        agent=agent,
        channel=channel,
        client_channel=client_channel,
        config_provider=provider,
        config=config,
        model=model,
        options=options,
    )
