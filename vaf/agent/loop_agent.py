"""LoopAgent - Multi-step loop execution strategy.

VAF simplified version of the original FiveLayerAgent.
Implements a basic loop: Plan -> Execute -> Verify pattern.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from vaf.agent.base import BaseAgent
from vaf.model.types import Message
from vaf.plan.types import Task, Step, Plan, RunResult
from vaf.tool.types import ToolResult

if TYPE_CHECKING:
    from vaf.memory.component import IMemory
    from vaf.model.component import IModelAdapter
    from vaf.tool.component import ITool


class LoopAgent(BaseAgent):
    """Loop-based agent implementation.
    
    Executes tasks using a Plan -> Execute -> Verify loop pattern.
    Simplified from the original FiveLayerAgent.
    
    This agent is suitable for:
    - Multi-step tasks
    - Tasks requiring tool usage
    - Tasks with retry requirements
    
    Example:
        agent = LoopAgent(
            name="my-agent",
            model=model,
            tools=[tool1, tool2],
        )
        result = await agent.run("Complete the given task")
    """

    def __init__(
        self,
        name: str,
        *,
        model: "IModelAdapter | None" = None,
        tools: list["ITool"] | None = None,
        memory: "IMemory | None" = None,
        system_prompt: str = "",
        max_iterations: int = 10,
    ) -> None:
        """Initialize the LoopAgent.
        
        Args:
            name: Agent identifier
            model: Model adapter for LLM interactions
            tools: List of tools available to the agent
            memory: Memory component
            system_prompt: System prompt for the agent
            max_iterations: Maximum loop iterations
        """
        super().__init__(
            name=name,
            model=model,
            tools=tools,
            memory=memory,
            system_prompt=system_prompt,
        )
        self._max_iterations = max_iterations
        self._run_id: str | None = None

    async def _execute(self, task: Task) -> RunResult:
        """Execute task using loop strategy."""
        self._run_id = uuid4().hex
        
        await self._log_event("loop.start", {
            "task_id": task.task_id,
            "run_id": self._run_id,
            "description": task.description,
        })
        
        # Emit pre-reply hook
        await self._emit_hook("agent.pre_reply", task)
        
        try:
            result = await self._run_loop(task)
        except Exception as e:
            result = RunResult(
                success=False,
                output=None,
                errors=[str(e)],
            )
        
        # Emit post-reply hook
        await self._emit_hook("agent.post_reply", task, result)
        
        await self._log_event("loop.complete", {
            "task_id": task.task_id,
            "run_id": self._run_id,
            "success": result.success,
        })
        
        return result

    async def _run_loop(self, task: Task) -> RunResult:
        """Run the main execution loop."""
        if self._model is None:
            return RunResult(
                success=False,
                errors=["No model configured"],
            )
        
        # Build conversation history
        messages: list[Message] = []
        
        # Add system prompt
        if self._system_prompt:
            messages.append(Message(role="system", content=self._system_prompt))
        
        # Add user task
        messages.append(Message(role="user", content=task.description))
        
        # Get tool definitions
        tool_definitions = self._tool_gateway.get_definitions() if self._tool_gateway else []
        
        last_output: Any = None
        errors: list[str] = []
        
        for iteration in range(self._max_iterations):
            # Generate response
            await self._emit_hook("model.pre_generate", messages)
            
            response = await self._model.generate(
                messages=messages,
                tools=tool_definitions if tool_definitions else None,
            )
            
            await self._emit_hook("model.post_generate", response)
            
            # Check if model wants to call tools
            if response.tool_calls:
                # Execute tool calls
                tool_results = await self._execute_tool_calls(response.tool_calls)
                
                # Add assistant message with tool calls
                messages.append(Message(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls,
                ))
                
                # Add tool results
                for tool_call, result in zip(response.tool_calls, tool_results):
                    messages.append(Message(
                        role="tool",
                        content=json.dumps(result.output) if result.success else (result.error or "Error"),
                        tool_call_id=tool_call.get("id", ""),
                    ))
                    
                    if not result.success and result.error:
                        errors.append(result.error)
                
                last_output = tool_results
            else:
                # No tool calls - model is done
                last_output = response.content
                messages.append(Message(
                    role="assistant",
                    content=response.content,
                ))
                break
        
        return RunResult(
            success=len(errors) == 0,
            output=last_output,
            errors=errors,
            metadata={
                "run_id": self._run_id,
                "task_id": task.task_id,
                "iterations": iteration + 1,
            },
        )

    async def _execute_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> list[ToolResult]:
        """Execute a list of tool calls.
        
        Args:
            tool_calls: List of tool call requests from the model
            
        Returns:
            List of tool results
        """
        results: list[ToolResult] = []
        
        for tool_call in tool_calls:
            func = tool_call.get("function", {})
            tool_name = func.get("name", "")
            
            # Parse arguments
            try:
                args_str = func.get("arguments", "{}")
                args = json.loads(args_str) if isinstance(args_str, str) else args_str
            except json.JSONDecodeError:
                results.append(ToolResult(
                    success=False,
                    error=f"Invalid JSON arguments for tool {tool_name}",
                ))
                continue
            
            # Emit pre-tool hook
            await self._emit_hook("tool.pre_call", tool_name, args)
            
            # Invoke tool
            if self._tool_gateway:
                result = await self._tool_gateway.invoke(tool_name, args)
            else:
                result = ToolResult(success=False, error="No tool gateway configured")
            
            # Emit post-tool hook
            await self._emit_hook("tool.post_call", tool_name, args, result)
            
            results.append(result)
        
        return results
