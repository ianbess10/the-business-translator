from __future__ import annotations

from src.config import Settings
from src.providers.base import ModelProvider
from src.providers.mock import MockProvider
from src.providers.openai_provider import OpenAIProvider


def get_provider(settings: Settings) -> ModelProvider:
    if settings.provider == "mock":
        return MockProvider()
    if settings.provider == "openai":
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            base_url=settings.openai_base_url,
            temperature=settings.temperature,
        )
    raise ValueError(
        f"Unsupported MODEL_PROVIDER={settings.provider!r}. "
        "Use 'mock' or 'openai'."
    )


__all__ = ["ModelProvider", "MockProvider", "OpenAIProvider", "get_provider"]
