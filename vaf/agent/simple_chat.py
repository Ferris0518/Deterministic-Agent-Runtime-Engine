"""SimpleChatAgent - Simple chat agent implementation.

A minimal agent for simple conversational interactions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from vaf.agent.base import BaseAgent
from vaf.model.types import Message
from vaf.plan.types import Task, RunResult

if TYPE_CHECKING:
    from vaf.memory.component import IMemory
    from vaf.model.component import IModelAdapter
    from vaf.tool.component import ITool


class SimpleChatAgent(BaseAgent):
    """Simple chat agent implementation.
    
    A minimal agent for simple conversational interactions without
    complex planning or multi-step orchestration.
    
    Suitable for:
    - Simple Q&A interactions
    - Single-turn conversations
    - Use cases where full loop orchestration is unnecessary
    
    Example:
        agent = SimpleChatAgent(
            name="chat-agent",
            model=model,
        )
        result = await agent.run("Hello, how are you?")
    """

    def __init__(
        self,
        name: str,
        *,
        model: "IModelAdapter | None" = None,
        tools: list["ITool"] | None = None,
        memory: "IMemory | None" = None,
        system_prompt: str = "",
    ) -> None:
        """Initialize the SimpleChatAgent.
        
        Args:
            name: Agent identifier
            model: Model adapter for LLM interactions
            tools: List of tools available to the agent
            memory: Memory component
            system_prompt: System prompt for the agent
        """
        super().__init__(
            name=name,
            model=model,
            tools=tools,
            memory=memory,
            system_prompt=system_prompt,
        )

    async def _execute(self, task: Task) -> RunResult:
        """Execute task using simple chat strategy.
        
        Simply sends the task to the model and returns the response.
        No planning or multi-step execution.
        """
        if self._model is None:
            return RunResult(
                success=False,
                errors=["No model configured"],
            )
        
        # Emit pre-reply hook
        await self._emit_hook("agent.pre_reply", task)
        
        # Build messages
        messages: list[Message] = []
        
        if self._system_prompt:
            messages.append(Message(role="system", content=self._system_prompt))
        
        messages.append(Message(role="user", content=task.description))
        
        # Generate response
        await self._emit_hook("model.pre_generate", messages)
        
        response = await self._model.generate(messages=messages)
        
        await self._emit_hook("model.post_generate", response)
        
        result = RunResult(
            success=True,
            output=response.content,
            metadata={
                "task_id": task.task_id,
            },
        )
        
        # Emit post-reply hook
        await self._emit_hook("agent.post_reply", task, result)
        
        return result
