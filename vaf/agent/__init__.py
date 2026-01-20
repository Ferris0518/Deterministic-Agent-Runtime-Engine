"""Agent module - User-facing API for VAF.

Classes:
    BaseAgent: Abstract base class for all agent implementations
    LoopAgent: Multi-step loop agent (Plan -> Execute -> Verify)
    SimpleChatAgent: Simple chat agent
"""

from vaf.agent.base import BaseAgent
from vaf.agent.loop_agent import LoopAgent
from vaf.agent.simple_chat import SimpleChatAgent

__all__ = [
    "BaseAgent",
    "LoopAgent",
    "SimpleChatAgent",
]
