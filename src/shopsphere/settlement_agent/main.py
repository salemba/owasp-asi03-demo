from __future__ import annotations

from shopsphere.settlement_agent.app import create_app
from shopsphere.settlement_agent.settings import SettlementAgentSettings

app = create_app(SettlementAgentSettings())
