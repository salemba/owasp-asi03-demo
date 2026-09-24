from __future__ import annotations

from shopsphere.common.llm.protocol import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        # TODO(step-N): Implement OpenAI integration behind protocol.
        return LLMResponse(text="OPENAI_PROVIDER_STUB")
