from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dare_framework.components.layer2 import IMCPClient

try:  # pragma: no cover - optional dependency
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamable_http_client
except Exception:  # pragma: no cover - optional dependency
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None
    streamable_http_client = None


class MCPUnavailableError(RuntimeError):
    pass


@dataclass
class StdioMCPConfig:
    command: str
    args: list[str]
    env: dict[str, str] | None = None


@dataclass
class StreamableHTTPConfig:
    url: str


class BaseMCPClient(IMCPClient):
    def __init__(self, name: str) -> None:
        self._name = name
        self._session: ClientSession | None = None
        self._client_cm = None

    @property
    def name(self) -> str:
        return self._name

    async def connect(self, server_config: dict[str, Any]) -> None:
        if ClientSession is None:
            raise MCPUnavailableError("mcp SDK is not installed")
        if self._session is not None:
            return
        if server_config:
            self._apply_server_config(server_config)
        await self._connect_session()

    async def disconnect(self) -> None:
        if self._session is None:
            return
        await self._session.__aexit__(None, None, None)
        self._session = None
        if self._client_cm is not None:
            await self._client_cm.__aexit__(None, None, None)
            self._client_cm = None

    async def list_tools(self) -> list[dict[str, Any]]:
        session = await self._require_session()
        result = await session.list_tools()
        tools = getattr(result, "tools", [])
        definitions: list[dict[str, Any]] = []
        for tool in tools:
            definitions.append(
                {
                    "name": getattr(tool, "name", ""),
                    "description": getattr(tool, "description", ""),
                    "input_schema": getattr(tool, "inputSchema", {}) or {},
                }
            )
        return definitions

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        session = await self._require_session()
        result = await session.call_tool(name, arguments=arguments)
        is_error = getattr(result, "isError", False)
        structured = getattr(result, "structuredContent", None)
        content_blocks = getattr(result, "content", [])
        text_chunks = [
            getattr(block, "text", "") for block in content_blocks if hasattr(block, "text")
        ]
        output = structured if structured is not None else {"content": text_chunks}
        return {
            "success": not is_error,
            "output": output,
            "error": "mcp tool error" if is_error else None,
        }

    async def _require_session(self) -> ClientSession:
        if self._session is None:
            await self.connect({})
        return self._session

    def _apply_server_config(self, server_config: dict[str, Any]) -> None:
        return None

    async def _connect_session(self) -> None:
        raise NotImplementedError


class StdioMCPClient(BaseMCPClient):
    def __init__(self, name: str, config: StdioMCPConfig) -> None:
        super().__init__(name)
        self._config = config

    @property
    def transport(self) -> str:
        return "stdio"

    def _apply_server_config(self, server_config: dict[str, Any]) -> None:
        if "command" in server_config:
            self._config.command = server_config["command"]
        if "args" in server_config:
            self._config.args = list(server_config["args"])
        if "env" in server_config:
            self._config.env = dict(server_config["env"])

    async def _connect_session(self) -> None:
        params = StdioServerParameters(
            command=self._config.command,
            args=self._config.args,
            env=self._config.env or {},
        )
        self._client_cm = stdio_client(params)
        read, write = await self._client_cm.__aenter__()
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        await self._session.initialize()


class StreamableHTTPMCPClient(BaseMCPClient):
    def __init__(self, name: str, config: StreamableHTTPConfig) -> None:
        super().__init__(name)
        self._config = config

    @property
    def transport(self) -> str:
        return "streamable_http"

    def _apply_server_config(self, server_config: dict[str, Any]) -> None:
        if "url" in server_config:
            self._config.url = server_config["url"]

    async def _connect_session(self) -> None:
        self._client_cm = streamable_http_client(self._config.url)
        read, write, _ = await self._client_cm.__aenter__()
        self._session = ClientSession(read, write)
        await self._session.__aenter__()
        await self._session.initialize()
