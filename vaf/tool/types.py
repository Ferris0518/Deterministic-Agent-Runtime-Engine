"""Tool domain data types.

VAF simplified version - only essential types retained.
Security types (RiskLevel, PolicyDecision) moved to security/types.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# =============================================================================
# Tool Definition
# =============================================================================

@dataclass(frozen=True)
class ToolDefinition:
    """Tool metadata exposed to models for function calling.
    
    Attributes:
        name: Unique tool name
        description: Human-readable description
        input_schema: JSON Schema for input validation
        output_schema: JSON Schema for output (optional)
    """
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] | None = None


# =============================================================================
# Tool Result
# =============================================================================

@dataclass(frozen=True)
class ToolResult:
    """Tool invocation result.
    
    Attributes:
        success: Whether the tool execution succeeded
        output: Tool output data
        error: Error message if failed
    """
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
