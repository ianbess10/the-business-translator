from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenerationRequest:
    system_prompt: str | None
    user_prompt: str
    expect_json: bool = False


@dataclass(frozen=True)
class GenerationResult:
    text: str
    provider: str
    model: str
    raw: dict[str, Any] | None = None


class ModelProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise NotImplementedError
