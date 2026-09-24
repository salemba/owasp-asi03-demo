from __future__ import annotations

from shopsphere.common.config import AppSettings


class SettlementAgentSettings(AppSettings):
    service_name: str = "settlement_agent"
    settlement_agent_ledger_url: str
