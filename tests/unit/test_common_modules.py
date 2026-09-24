from __future__ import annotations

from decimal import Decimal

import pytest

from shopsphere.common.config import AppSettings
from shopsphere.common.db import create_engine, create_session_factory
from shopsphere.common.errors import DependencyUnavailableError, ShopSphereError
from shopsphere.common.llm import AnthropicProvider, MockProvider, OpenAIProvider
from shopsphere.common.llm.protocol import LLMResponse
from shopsphere.common.logging import get_logger
from shopsphere.common.providers import get_llm_provider


@pytest.mark.unit
def test_database_dsn_builds_from_settings() -> None:
    settings = AppSettings(
        database_password="password",
        openai_api_key="openai",
        anthropic_api_key="anthropic",
    )
    assert settings.database_dsn.startswith("postgresql+asyncpg://")


@pytest.mark.unit
def test_db_factories_return_objects() -> None:
    settings = AppSettings(
        database_password="password",
        openai_api_key="openai",
        anthropic_api_key="anthropic",
    )
    engine = create_engine(settings)
    session_factory = create_session_factory(settings)
    assert engine.url.render_as_string(hide_password=False).startswith("postgresql+asyncpg://")
    assert session_factory is not None


@pytest.mark.unit
def test_llm_provider_selection_uses_mock_default() -> None:
    mock_settings = AppSettings(
        database_password="password",
        openai_api_key="openai",
        anthropic_api_key="anthropic",
        llm_provider="unknown",
    )
    openai_settings = AppSettings(
        database_password="password",
        openai_api_key="openai",
        anthropic_api_key="anthropic",
        llm_provider="openai",
    )
    anthropic_settings = AppSettings(
        database_password="password",
        openai_api_key="openai",
        anthropic_api_key="anthropic",
        llm_provider="anthropic",
    )

    assert isinstance(get_llm_provider(mock_settings), MockProvider)
    assert isinstance(get_llm_provider(openai_settings), OpenAIProvider)
    assert isinstance(get_llm_provider(anthropic_settings), AnthropicProvider)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_stubs_return_deterministic_text() -> None:
    prompt = "hello"
    mock_response = await MockProvider().generate(prompt)
    openai_response = await OpenAIProvider().generate(prompt)
    anthropic_response = await AnthropicProvider().generate(prompt)

    assert mock_response == LLMResponse(text="MOCK_RESPONSE::hello")
    assert openai_response.text == "OPENAI_PROVIDER_STUB"
    assert anthropic_response.text == "ANTHROPIC_PROVIDER_STUB"


@pytest.mark.unit
def test_error_types_and_logger_helper() -> None:
    assert issubclass(DependencyUnavailableError, ShopSphereError)
    logger = get_logger("shopsphere.test")
    logger.info("coverage-check", amount=str(Decimal("1.00")))
