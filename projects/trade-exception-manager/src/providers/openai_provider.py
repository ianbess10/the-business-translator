from __future__ import annotations

import os
from typing import Any

from src.providers.base import GenerationRequest, GenerationResult, ModelProvider

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


class OpenAIProvider(ModelProvider):
    """OpenAI-compatible chat provider. API key must come from environment."""

    name = "openai"

    def __init__(
        self,
        api_key: str | None,
        model: str,
        base_url: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when MODEL_PROVIDER=openai. "
                "Copy .env.example to .env and set the key, or switch to MODEL_PROVIDER=mock."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The openai package is required for MODEL_PROVIDER=openai. "
                "Install dependencies from requirements.txt."
            ) from exc

        # The OpenAI SDK also reads OPENAI_BASE_URL from the process env. An empty
        # value from .env ("OPENAI_BASE_URL=") becomes an invalid client base URL.
        resolved_base_url = (base_url or "").strip() or DEFAULT_OPENAI_BASE_URL
        if not resolved_base_url.startswith(("http://", "https://")):
            raise ValueError(
                "OPENAI_BASE_URL must start with http:// or https:// "
                f"(received {resolved_base_url!r})."
            )
        if not (os.getenv("OPENAI_BASE_URL") or "").strip():
            os.environ.pop("OPENAI_BASE_URL", None)

        self._client = OpenAI(api_key=api_key, base_url=resolved_base_url)
        self._model = model
        self._temperature = temperature

    def generate(self, request: GenerationRequest) -> GenerationResult:
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.user_prompt})

        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
        }
        if request.expect_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = self._client.chat.completions.create(**kwargs)
        text = (response.choices[0].message.content or "").strip()
        raw = response.model_dump() if hasattr(response, "model_dump") else None
        return GenerationResult(
            text=text,
            provider=self.name,
            model=self._model,
            raw=raw,
        )
