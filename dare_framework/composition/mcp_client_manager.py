from __future__ import annotations

from dare_framework.composition.base_component_manager import BaseComponentManager, EntryPointLoader, ENTRYPOINT_MCP_CLIENTS
from dare_framework.core.mcp.mcp_client import IMCPClient


class MCPClientManager(BaseComponentManager[IMCPClient]):
    def __init__(self, entry_points_loader: EntryPointLoader | None = None) -> None:
        super().__init__(ENTRYPOINT_MCP_CLIENTS, IMCPClient, entry_points_loader, config_section="mcp")
