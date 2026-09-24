from __future__ import annotations

from shopsphere.common.config import AppSettings
from shopsphere.common.llm import AnthropicProvider, LLMProvider, MockProvider, OpenAIProvider


def get_llm_provider(settings: AppSettings) -> LLMProvider:
    provider_name = settings.llm_provider.lower()
    if provider_name == "openai":
        return OpenAIProvider()
    if provider_name == "anthropic":
        return AnthropicProvider()
    return MockProvider()
