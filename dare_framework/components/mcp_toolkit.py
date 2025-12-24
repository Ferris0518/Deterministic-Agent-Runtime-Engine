from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from dare_framework.components.interfaces import IMCPClient, ITool
from dare_framework.core.models import RiskLevel, RunContext, ToolResult, ToolType


@dataclass
class MCPTool(ITool):
    def __init__(self, client: IMCPClient, definition: dict[str, Any]) -> None:
        self._client = client
        self._definition = definition

    @property
    def name(self) -> str:
        return str(self._definition.get("name", ""))

    @property
    def description(self) -> str:
        return str(self._definition.get("description", ""))

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ATOMIC

    @property
    def risk_level(self) -> RiskLevel:
        value = self._definition.get("risk_level")
        if isinstance(value, RiskLevel):
            return value
        try:
            return RiskLevel(str(value))
        except Exception:
            return RiskLevel.READ_ONLY

    def get_input_schema(self) -> dict[str, Any]:
        return (
            self._definition.get("input_schema")
            or self._definition.get("inputSchema")
            or {}
        )

    async def execute(self, input: dict[str, Any], ctx: RunContext) -> ToolResult:
        result = await self._client.call_tool(self.name, arguments=input)
        if isinstance(result, dict) and "success" in result:
            output = result.get("output", {})
            return ToolResult(
                success=bool(result.get("success")),
                output=output,
                error=result.get("error"),
                evidence_ref=result.get("evidence_ref"),
            )
        return ToolResult(success=True, output=result)


class MCPToolkit:
    def __init__(self, clients: Iterable[IMCPClient]) -> None:
        self._clients = list(clients)
        self._tools: list[MCPTool] = []

    async def initialize(self) -> None:
        for client in self._clients:
            await client.connect({})
            for tool_def in await client.list_tools():
                self._tools.append(MCPTool(client, tool_def))

    async def disconnect(self) -> None:
        for client in self._clients:
            await client.disconnect()

    def export_tools(self) -> list[ITool]:
        return list(self._tools)
