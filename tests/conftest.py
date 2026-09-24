from __future__ import annotations

import os


def pytest_configure() -> None:
    defaults = {
        "SHOPSPHERE_DATABASE_PASSWORD": "test-password",
        "SHOPSPHERE_OPENAI_API_KEY": "test-openai",
        "SHOPSPHERE_ANTHROPIC_API_KEY": "test-anthropic",
        "SHOPSPHERE_GATEWAY_SUPPORT_AGENT_URL": "http://support-agent:8000",
        "SHOPSPHERE_SUPPORT_AGENT_SETTLEMENT_AGENT_URL": "http://settlement-agent:8000",
        "SHOPSPHERE_SETTLEMENT_AGENT_LEDGER_URL": "http://mcp-ledger:8000",
        "SHOPSPHERE_KEYCLOAK_ISSUER_URL": "http://keycloak:8080/realms/shopsphere",
        "SHOPSPHERE_KEYCLOAK_CLIENT_ID": "gateway",
        "SHOPSPHERE_KEYCLOAK_CLIENT_SECRET": "test-secret",
        "SHOPSPHERE_TELEMETRY_ENABLED": "false",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)
