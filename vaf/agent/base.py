"""BaseAgent - Abstract base class for all agent implementations.

VAF simplified version with built-in hooks support.

BaseAgent provides:
- Component assembly (tools, model, memory)
- Built-in hooks system (class-level and instance-level)
- Abstract _execute() method for subclasses
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from vaf.plan.types import Task, RunResult
from vaf.event.types import HookType

if TYPE_CHECKING:
    from vaf.context.component import IContextManager
    from vaf.memory.component import IMemory
    from vaf.model.component import IModelAdapter
    from vaf.event.component import IEventLog
    from vaf.tool.component import ITool, IToolGateway


class BaseAgent(ABC):
    """Abstract base class for all agent implementations.
    
    Features:
    - Component assembly with sensible defaults
    - Built-in hooks system (class-level + instance-level)
    - Abstract _execute() method for custom strategies
    
    Hooks:
    - Class-level hooks affect all instances
    - Instance-level hooks affect only one instance
    - Supported hook types: agent.pre_reply, agent.post_reply, 
      tool.pre_call, tool.post_call
    
    Example:
        class MyAgent(BaseAgent):
            async def _execute(self, task: Task) -> RunResult:
                # Custom execution logic
                ...
        
        # Register class-level hook
        MyAgent.register_hook("agent.pre_reply", "logger", my_logger)
        
        # Create agent and register instance-level hook
        agent = MyAgent(name="my-agent", model=model)
        agent.add_hook("agent.post_reply", "trace", my_tracer)
    """

    # Supported hook types
    HOOK_TYPES: list[HookType] = [
        "agent.pre_reply",
        "agent.post_reply",
        "tool.pre_call",
        "tool.post_call",
        "model.pre_generate",
        "model.post_generate",
    ]
    
    # Class-level hooks (shared by all instances)
    _class_hooks: dict[str, dict[str, Callable[..., Any]]] = {
        "agent.pre_reply": {},
        "agent.post_reply": {},
        "tool.pre_call": {},
        "tool.post_call": {},
        "model.pre_generate": {},
        "model.post_generate": {},
    }

    def __init__(
        self,
        name: str,
        *,
        model: "IModelAdapter | None" = None,
        tools: list["ITool"] | None = None,
        memory: "IMemory | None" = None,
        system_prompt: str = "",
    ) -> None:
        """Initialize the agent.
        
        Args:
            name: Agent identifier
            model: Model adapter for LLM interactions
            tools: List of tools available to the agent
            memory: Memory component for context persistence
            system_prompt: System prompt for the agent
        """
        self._name = name
        self._system_prompt = system_prompt
        
        # Store user-provided components
        self._user_model = model
        self._user_tools = tools or []
        self._user_memory = memory
        
        # Instance-level hooks
        self._hooks: dict[str, dict[str, Callable[..., Any]]] = {
            hook_type: {} for hook_type in self.HOOK_TYPES
        }
        
        # Built components (lazy initialization)
        self._model: "IModelAdapter | None" = None
        self._tool_gateway: "IToolGateway | None" = None
        self._memory: "IMemory | None" = None
        self._context_manager: "IContextManager | None" = None
        self._event_log: "IEventLog | None" = None
        
        # Build components
        self._build_components()

    @property
    def name(self) -> str:
        """Agent name identifier."""
        return self._name
    
    @property
    def system_prompt(self) -> str:
        """Agent system prompt."""
        return self._system_prompt

    # =========================================================================
    # Hook System
    # =========================================================================

    @classmethod
    def register_hook(
        cls,
        hook_type: HookType,
        name: str,
        callback: Callable[..., Any],
    ) -> None:
        """Register a class-level hook (affects all instances).
        
        Args:
            hook_type: Type of hook
            name: Unique hook name
            callback: The callback function
        """
        if hook_type not in cls._class_hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
        cls._class_hooks[hook_type][name] = callback
    
    @classmethod
    def remove_hook(cls, hook_type: HookType, name: str) -> None:
        """Remove a class-level hook.
        
        Args:
            hook_type: Type of hook
            name: Hook name to remove
        """
        if hook_type in cls._class_hooks and name in cls._class_hooks[hook_type]:
            del cls._class_hooks[hook_type][name]
    
    @classmethod
    def clear_hooks(cls, hook_type: HookType | None = None) -> None:
        """Clear class-level hooks.
        
        Args:
            hook_type: Type to clear, or None to clear all
        """
        if hook_type is None:
            for ht in cls._class_hooks:
                cls._class_hooks[ht].clear()
        elif hook_type in cls._class_hooks:
            cls._class_hooks[hook_type].clear()

    def add_hook(
        self,
        hook_type: HookType,
        name: str,
        callback: Callable[..., Any],
    ) -> None:
        """Register an instance-level hook.
        
        Args:
            hook_type: Type of hook
            name: Unique hook name
            callback: The callback function
        """
        if hook_type not in self._hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
        self._hooks[hook_type][name] = callback
    
    def remove_instance_hook(self, hook_type: HookType, name: str) -> None:
        """Remove an instance-level hook.
        
        Args:
            hook_type: Type of hook
            name: Hook name to remove
        """
        if hook_type in self._hooks and name in self._hooks[hook_type]:
            del self._hooks[hook_type][name]

    async def _emit_hook(self, hook_type: HookType, *args: Any, **kwargs: Any) -> None:
        """Trigger all hooks of a given type.
        
        Class-level hooks are triggered first, then instance-level hooks.
        
        Args:
            hook_type: Type of hook to trigger
            *args: Arguments to pass to hooks
            **kwargs: Keyword arguments to pass to hooks
        """
        # Class-level hooks
        for callback in self._class_hooks.get(hook_type, {}).values():
            try:
                result = callback(self, *args, **kwargs)
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass  # Don't let hook errors break execution
        
        # Instance-level hooks
        for callback in self._hooks.get(hook_type, {}).values():
            try:
                result = callback(*args, **kwargs)
                if hasattr(result, "__await__"):
                    await result
            except Exception:
                pass

    # =========================================================================
    # Run Method
    # =========================================================================

    async def run(self, task: str | Task) -> RunResult:
        """Run a task and return the result.
        
        Args:
            task: The task to run (string description or Task object)
            
        Returns:
            The execution result
        """
        # Convert string to Task if needed
        task_obj = task if isinstance(task, Task) else Task(description=task)
        
        # Delegate to subclass implementation
        return await self._execute(task_obj)

    @abstractmethod
    async def _execute(self, task: Task) -> RunResult:
        """Execute the task with the agent's specific strategy.
        
        Subclasses must implement this method.
        
        Args:
            task: The task to execute
            
        Returns:
            The execution result
        """
        ...

    # =========================================================================
    # Component Building
    # =========================================================================

    def _build_components(self) -> None:
        """Build all components."""
        self._model = self._user_model
        self._memory = self._build_memory()
        self._tool_gateway = self._build_tool_gateway()
        self._event_log = self._build_event_log()
        self._context_manager = self._build_context_manager()

    def _build_memory(self) -> "IMemory | None":
        """Build memory component."""
        if self._user_memory is not None:
            return self._user_memory
        # Default: use NoOpMemory
        from vaf.memory.impl.noop_memory import NoOpMemory
        return NoOpMemory()

    def _build_tool_gateway(self) -> "IToolGateway":
        """Build tool gateway."""
        from vaf.tool.impl.default_tool_gateway import DefaultToolGateway
        gateway = DefaultToolGateway()
        for tool in self._user_tools:
            gateway.register_tool(tool)
        return gateway

    def _build_event_log(self) -> "IEventLog":
        """Build event log."""
        from vaf.event.impl.local_event_log import LocalEventLog
        return LocalEventLog(path=f".vaf/{self._name}/events.jsonl")

    def _build_context_manager(self) -> "IContextManager":
        """Build context manager."""
        from vaf.context.impl.default_context_manager import DefaultContextManager
        return DefaultContextManager(memory=self._memory)

    # =========================================================================
    # Logging Helper
    # =========================================================================

    async def _log_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Log an event to the event log.
        
        Args:
            event_type: Type of event
            payload: Event data
        """
        if self._event_log is not None:
            await self._event_log.append(event_type, payload)
