"""OpenRouter model adapter using OpenAI SDK."""
from __future__ import annotations

import os
from typing import Any

from dare_framework.model import Prompt, ModelResponse


class OpenRouterModelAdapter:
    """Model adapter for OpenRouter API (compatible with OpenAI SDK)."""

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None):
        """Initialize OpenRouter adapter.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var).
            model: Model name (defaults to OPENROUTER_MODEL env var).
            base_url: API base URL (defaults to OPENROUTER_BASE_URL env var).
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2-flash:free")
        self.base_url = base_url or os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")

        # Lazy import to avoid dependency if not using OpenRouter mode
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise ImportError(
                "OpenAI SDK is required for OpenRouter. Install with: pip install openai"
            ) from e

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def generate(self, prompt: Prompt, **kwargs: Any) -> ModelResponse:
        """Generate a response using OpenRouter.

        Args:
            prompt: The prompt to generate from.
            **kwargs: Additional generation options.

        Returns:
            ModelResponse with generated content.
        """
        # Convert Prompt to OpenAI messages format
        messages = []
        for msg in prompt.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        # Call OpenRouter API
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            **kwargs
        )

        # Extract response
        content = response.choices[0].message.content or ""

        return ModelResponse(
            content=content,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            metadata={
                "model": self.model_name,
                "finish_reason": response.choices[0].finish_reason,
            }
        )
