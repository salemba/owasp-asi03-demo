from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class LLMResponse(BaseModel):
    text: str


class LLMProvider(Protocol):
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate a response for a prompt."""
