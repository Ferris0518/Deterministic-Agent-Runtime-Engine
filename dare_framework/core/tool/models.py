from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dare_framework.core.models.evidence import Evidence
from dare_framework.core.risk_level import RiskLevel
from dare_framework.core.tool.enums import ToolType


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    tool_type: ToolType = ToolType.ATOMIC
    risk_level: RiskLevel = RiskLevel.READ_ONLY
    requires_approval: bool = False
    timeout_seconds: int = 30
    produces_assertions: list[dict[str, Any]] = field(default_factory=list)
    is_work_unit: bool = False


@dataclass(frozen=True)
class ToolResult:
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    evidence: list[Evidence] = field(default_factory=list)


@dataclass
class ToolErrorRecord:
    error_type: str
    tool_name: str
    message: str
    user_hint: str | None = None

