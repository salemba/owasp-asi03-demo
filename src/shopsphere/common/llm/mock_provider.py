from __future__ import annotations

from shopsphere.common.llm.protocol import LLMProvider, LLMResponse


class MockProvider(LLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(text=f"MOCK_RESPONSE::{prompt}")
