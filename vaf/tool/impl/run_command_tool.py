"""Run command tool implementation."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from vaf.tool.component import ITool
from vaf.tool.types import ToolResult, ToolDefinition


class RunCommandTool:
    """Execute a shell command within an allowed workspace root.
    
    Implements the ITool interface.
    """

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return "Execute a shell command within an allowed workspace root."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute"},
                "cwd": {"type": "string", "description": "Working directory (optional)"},
                "timeout_seconds": {"type": "integer", "minimum": 1, "description": "Timeout in seconds"},
            },
            "required": ["command"],
        }

    def get_definition(self) -> ToolDefinition:
        """Get tool definition for model function calling."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
        )

    async def execute(self, params: dict[str, Any]) -> ToolResult:
        """Execute the shell command."""
        command = params.get("command")
        if not isinstance(command, str) or not command.strip():
            return ToolResult(success=False, error="command is required")

        cwd = params.get("cwd")
        if cwd:
            cwd = Path(cwd).expanduser().resolve()
        else:
            cwd = Path.cwd()

        timeout = params.get("timeout_seconds", 30)
        try:
            timeout = int(timeout)
        except (TypeError, ValueError):
            timeout = 30

        proc: asyncio.subprocess.Process | None = None
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=str(cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            if proc and proc.returncode is None:
                proc.kill()
                await proc.communicate()
            return ToolResult(success=False, error="command timed out")
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))

        return ToolResult(
            success=proc.returncode == 0,
            output={
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "exit_code": proc.returncode,
            },
            error=None if proc.returncode == 0 else "command failed",
        )
