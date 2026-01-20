"""Error types for VAF."""


class ToolError(Exception):
    """Base exception for tool-related errors."""
    pass


class ToolNotFoundError(Exception):
    """Raised when a requested tool is not found."""
    pass


class ToolAccessDenied(Exception):
    """Raised when access to a tool is denied."""
    pass


class ApprovalRequired(Exception):
    """Raised when human approval is required."""
    pass


class ResourceExhausted(RuntimeError):
    """Raised when a budget limit is exceeded."""
    pass
