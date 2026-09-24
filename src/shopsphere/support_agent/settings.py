from __future__ import annotations

from shopsphere.common.config import AppSettings


class SupportAgentSettings(AppSettings):
    service_name: str = "support_agent"
    support_agent_settlement_agent_url: str
