"""VAF - Versatile Agent Framework.

A simplified, industrial-grade AI Agent execution framework.

Architecture (8 modules):
- agent/: User API layer (BaseAgent, LoopAgent, SimpleChatAgent)
- model/: LLM adapter interfaces
- tool/: Tool execution
- memory/: Memory and context persistence
- context/: Context management
- plan/: Task and planning types
- event/: Audit logging and hooks
- security/: Security boundary

Usage:
    from vaf import LoopAgent, Task
    
    agent = LoopAgent(name="my_agent", model=model, tools=[tool1, tool2])
    result = await agent.run("Complete this task")
"""

from vaf.agent import BaseAgent, LoopAgent, SimpleChatAgent
from vaf.plan.types import Task, Step, Plan, RunResult
from vaf.model.types import Message, ModelResponse
from vaf.tool.types import ToolResult, ToolDefinition

__all__ = [
    # Agent classes
    "BaseAgent",
    "LoopAgent",
    "SimpleChatAgent",
    # Plan types
    "Task",
    "Step",
    "Plan",
    "RunResult",
    # Model types
    "Message",
    "ModelResponse",
    # Tool types
    "ToolResult",
    "ToolDefinition",
]

__version__ = "1.0.0"
