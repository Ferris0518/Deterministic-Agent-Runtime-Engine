from __future__ import annotations

from typing import Any
import json

from ...core.config import IPromptStore
from ...core.context import IModelAdapter
from ...core.models.config import ComponentType, Config
from ...core.models.context import GenerateOptions, Message, ModelResponse
from ...core.models.tool import ToolDefinition
from ..base_component import ConfigurableComponent

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
except ImportError:  # pragma: no cover - handled at runtime
    ChatOpenAI = None  # type: ignore[assignment]
    AIMessage = None  # type: ignore[assignment]
    HumanMessage = None  # type: ignore[assignment]
    SystemMessage = None  # type: ignore[assignment]
    ToolMessage = None  # type: ignore[assignment]


class OpenAIModelAdapter(ConfigurableComponent, IModelAdapter):
    component_type = ComponentType.MODEL_ADAPTER

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._endpoint = endpoint
        self._extra: dict[str, Any] = {}
        self._client = None

    async def init(self, config: Config | None = None, prompts: IPromptStore | None = None) -> None:
        if config is not None:
            llm = config.llm
            if self._model is None:
                self._model = llm.model
            if self._api_key is None:
                self._api_key = llm.api_key
            if self._endpoint is None:
                self._endpoint = llm.endpoint
            self._extra = dict(llm.extra)
        self._client = self._build_client()

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        options: GenerateOptions | None = None,
    ) -> ModelResponse:
        client = self._ensure_client()
        client = self._apply_options(client, options)
        if tools:
            client = client.bind_tools([self._tool_definition(tool) for tool in tools])
        response = await client.ainvoke(self._to_langchain_messages(messages))
        tool_calls = self._extract_tool_calls(response)
        return ModelResponse(content=response.content or "", tool_calls=tool_calls)

    async def generate_structured(self, messages: list[Message], output_schema: type[Any]) -> Any:
        client = self._ensure_client()
        if hasattr(client, "with_structured_output"):
            structured = client.with_structured_output(output_schema)
            return await structured.ainvoke(self._to_langchain_messages(messages))
        try:
            return output_schema()
        except Exception:  # noqa: BLE001
            return {}

    def _ensure_client(self) -> Any:
        if self._client is None:
            self._client = self._build_client()
        return self._client

    def _build_client(self) -> Any:
        if ChatOpenAI is None:
            raise RuntimeError("langchain-openai is required for OpenAIModelAdapter")
        model = self._model or "gpt-4o-mini"
        kwargs: dict[str, Any] = {"model": model}
        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._endpoint:
            kwargs["base_url"] = self._endpoint
        kwargs.update(self._extra)
        return ChatOpenAI(**kwargs)

    def _to_langchain_messages(self, messages: list[Message]) -> list[Any]:
        mapped = []
        for msg in messages:
            if msg.role == "system":
                mapped.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                mapped.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                tool_calls = self._normalize_tool_calls_for_langchain(msg.tool_calls or [])
                mapped.append(AIMessage(content=msg.content, tool_calls=tool_calls))
            elif msg.role == "tool":
                tool_call_id = msg.tool_call_id or "tool_call"
                mapped.append(ToolMessage(content=msg.content, tool_call_id=tool_call_id))
            else:
                mapped.append(HumanMessage(content=msg.content))
        return mapped

    def _apply_options(self, client: Any, options: GenerateOptions | None) -> Any:
        if options is None:
            return client
        bind_kwargs = {}
        if options.max_tokens is not None:
            bind_kwargs["max_tokens"] = options.max_tokens
        if options.temperature is not None:
            bind_kwargs["temperature"] = options.temperature
        if not bind_kwargs:
            return client
        return client.bind(**bind_kwargs)

    def _extract_tool_calls(self, response: Any) -> list[dict[str, Any]]:
        raw_calls = getattr(response, "tool_calls", None)
        if not raw_calls:
            raw_calls = getattr(response, "additional_kwargs", {}).get("tool_calls", [])
        normalized = []
        for call in raw_calls or []:
            name, args, call_id = self._extract_tool_call_fields(call)
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {"raw": args}
            if args is None:
                args = {}
            normalized.append({"id": call_id, "name": name, "arguments": args})
        return normalized

    def _extract_tool_call_fields(self, call: Any) -> tuple[str | None, Any, str | None]:
        if isinstance(call, dict):
            name = call.get("name") or call.get("function", {}).get("name")
            args = call.get("args") or call.get("arguments") or call.get("function", {}).get("arguments")
            call_id = call.get("id") or call.get("tool_call_id")
        else:
            name = getattr(call, "name", None)
            args = getattr(call, "args", None) or getattr(call, "arguments", None)
            call_id = getattr(call, "id", None)
        return name, args, call_id

    def _normalize_tool_calls_for_langchain(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        normalized = []
        for call in tool_calls:
            if not isinstance(call, dict):
                continue
            normalized.append(
                {
                    "id": call.get("id"),
                    "name": call.get("name"),
                    "args": call.get("arguments") if "arguments" in call else call.get("args", {}),
                }
            )
        return normalized

    def _tool_definition(self, tool: ToolDefinition) -> dict[str, Any]:
        parameters = tool.input_schema or {"type": "object", "properties": {}}
        if "type" not in parameters:
            parameters = {"type": "object", "properties": parameters}
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": parameters,
            },
        }
