"""LLM-based remediator implementation.

This remediator uses a model adapter to analyze verification failures
and generate guidance for the next plan attempt.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from dare_framework.context.kernel import IContext
from dare_framework.context.types import Message
from dare_framework.infra.component import ComponentType
from dare_framework.model.kernel import IModelAdapter
from dare_framework.model.types import GenerateOptions, ModelInput, ModelResponse
from dare_framework.plan.interfaces import IRemediator
from dare_framework.plan.types import VerifyResult


DEFAULT_REMEDIATION_PROMPT = """You are a remediation advisor. Given a failed verification result,
analyze what went wrong and provide concise guidance for the next planning attempt.

Respond with a JSON object in this exact format:
{
    "reflection": "Brief analysis of what went wrong and what to try differently",
    "suggestions": ["specific suggestion 1", "specific suggestion 2"]
}

Guidelines:
- Be specific about what failed
- Suggest concrete alternatives
- Keep reflection under 200 words
- Focus on actionable changes"""


class LLMRemediator(IRemediator):
    """LLM-based remediator that analyzes failures and generates guidance.

    This remediator:
    1. Takes the verification failure result
    2. Uses LLM to analyze what went wrong
    3. Generates a reflection string to guide the next planning attempt
    """

    def __init__(
        self,
        model_adapter: IModelAdapter,
        system_prompt: str | None = None,
        name: str = "llm_remediator",
        temperature: float = 0.3,
        max_tokens: int | None = 500,
    ) -> None:
        """Initialize the LLM remediator.

        Args:
            model_adapter: The model adapter to use for generation
            system_prompt: Custom system prompt (uses default if None)
            name: Component name for config lookups
            temperature: Generation temperature
            max_tokens: Max tokens for generation
        """
        self._model = model_adapter
        self._system_prompt = system_prompt or DEFAULT_REMEDIATION_PROMPT
        self._name = name
        self._temperature = temperature
        self._max_tokens = max_tokens

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.REMEDIATOR]:
        """Component category for config scoping."""
        return ComponentType.REMEDIATOR

    async def remediate(self, verify_result: VerifyResult, ctx: IContext) -> str:
        """Generate remediation guidance for a failed verification.

        Args:
            verify_result: The verification result containing errors
            ctx: The execution context

        Returns:
            A reflection string to guide the next planning attempt
        """
        # Get context info
        metadata = ctx.config or {}
        milestone_id = metadata.get("milestone_id", "milestone_001")
        attempt = metadata.get("plan_attempt", 0)

        # Build the remediation prompt
        messages = [
            Message(role="system", content=self._system_prompt),
            Message(
                role="user",
                content=self._build_remediation_prompt(verify_result, attempt),
            ),
        ]

        # Create model input
        model_input = ModelInput(
            messages=messages,
            tools=[],
            metadata={
                "purpose": "remediation",
                "milestone_id": milestone_id,
                "attempt": attempt,
            },
        )

        # Call model
        options = GenerateOptions(
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        response = await self._model.generate(model_input, options=options)

        # Parse and return reflection
        return self._parse_remediation_response(response)

    def _build_remediation_prompt(
        self, verify_result: VerifyResult, attempt: int
    ) -> str:
        """Build the remediation prompt with failure details."""
        errors_text = "\n".join(
            f"- {error}" for error in verify_result.errors
        ) if verify_result.errors else "No specific errors provided"

        metadata_text = ""
        if verify_result.metadata:
            metadata_text = f"\nAdditional metadata: {json.dumps(verify_result.metadata, indent=2)}"

        return f"""Verification failed on attempt {attempt}.

Errors:
{errors_text}{metadata_text}

Analyze the failure and provide guidance for the next planning attempt.

Respond with JSON:
{{
    "reflection": "Your analysis here",
    "suggestions": ["suggestion 1", "suggestion 2"]
}}"""

    def _parse_remediation_response(self, response: ModelResponse) -> str:
        """Parse model response into a reflection string."""
        content = response.content or ""

        # Try to extract JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            data = self._extract_json_from_markdown(content)

        if isinstance(data, dict):
            reflection = data.get("reflection", "")
            suggestions = data.get("suggestions", [])

            if reflection:
                if suggestions:
                    suggestions_text = "\n".join(
                        f"- {s}" for s in suggestions
                    )
                    return f"{reflection}\n\nSuggestions:\n{suggestions_text}"
                return reflection

        # Fallback: return the raw content if parsing fails
        return content if content else "No specific guidance available. Retry with different approach."

    def _extract_json_from_markdown(self, content: str) -> dict[str, Any]:
        """Extract JSON from markdown code blocks."""
        import re

        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"\{.*\}",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue

        return {}


class SimpleRemediator(IRemediator):
    """Simple rule-based remediator for basic failure scenarios.

    This remediator provides deterministic guidance based on error patterns,
    suitable for testing and simple scenarios without LLM calls.
    """

    def __init__(self, name: str = "simple_remediator") -> None:
        self._name = name

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.REMEDIATOR]:
        """Component category for config scoping."""
        return ComponentType.REMEDIATOR

    async def remediate(self, verify_result: VerifyResult, ctx: IContext) -> str:
        """Generate simple remediation guidance based on error patterns."""
        errors = verify_result.errors

        if not errors:
            return "Verification failed without specific errors. Review execution output."

        # Pattern-based guidance
        guidance_parts: list[str] = []

        for error in errors:
            error_lower = error.lower()

            if "unknown capability" in error_lower:
                guidance_parts.append(
                    "A tool was referenced that doesn't exist in the registry. "
                    "Use only available tools from the tool list."
                )
            elif "missing required" in error_lower:
                guidance_parts.append(
                    "A required parameter was missing. Ensure all required fields are provided."
                )
            elif "schema" in error_lower or "type" in error_lower:
                guidance_parts.append(
                    "Parameter type mismatch. Check that parameters match the expected types."
                )
            elif "permission" in error_lower or "not allowed" in error_lower:
                guidance_parts.append(
                    "Operation not permitted. Consider using a different approach or tool."
                )
            elif "timeout" in error_lower:
                guidance_parts.append(
                    "Operation timed out. Consider breaking into smaller steps."
                )
            else:
                guidance_parts.append(f"Error: {error}")

        # Get unique guidance messages
        unique_guidance = list(dict.fromkeys(guidance_parts))

        reflection = "\n".join(f"- {g}" for g in unique_guidance)
        return f"Issues identified:\n{reflection}\n\nTry a revised approach addressing these points."


class NoOpRemediator(IRemediator):
    """No-op remediator that returns empty guidance.

    Useful when remediation is handled externally or not needed.
    """

    def __init__(self, name: str = "noop_remediator") -> None:
        self._name = name

    @property
    def name(self) -> str:
        """Stable name for config lookups."""
        return self._name

    @property
    def component_type(self) -> Literal[ComponentType.REMEDIATOR]:
        """Component category for config scoping."""
        return ComponentType.REMEDIATOR

    async def remediate(self, verify_result: VerifyResult, ctx: IContext) -> str:
        """Return empty remediation guidance."""
        return ""


__all__ = [
    "LLMRemediator",
    "NoOpRemediator",
    "SimpleRemediator",
    "DEFAULT_REMEDIATION_PROMPT",
]
