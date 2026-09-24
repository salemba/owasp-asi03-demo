from __future__ import annotations

from shopsphere.common.llm.protocol import LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        # TODO(step-N): Implement Anthropic integration behind protocol.
        return LLMResponse(text="ANTHROPIC_PROVIDER_STUB")
