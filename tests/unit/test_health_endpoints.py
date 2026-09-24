from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shopsphere.finance_approval.app import create_app as create_finance_app
from shopsphere.finance_approval.settings import FinanceApprovalSettings
from shopsphere.gateway.app import create_app as create_gateway_app
from shopsphere.gateway.settings import GatewaySettings
from shopsphere.mcp_servers.crm.app import create_app as create_crm_app
from shopsphere.mcp_servers.crm.settings import CrmMCPSettings
from shopsphere.mcp_servers.ledger.app import create_app as create_ledger_app
from shopsphere.mcp_servers.ledger.settings import LedgerMCPSettings
from shopsphere.mcp_servers.orders.app import create_app as create_orders_app
from shopsphere.mcp_servers.orders.settings import OrdersMCPSettings
from shopsphere.mcp_servers.payments.app import create_app as create_payments_app
from shopsphere.mcp_servers.payments.settings import PaymentsMCPSettings
from shopsphere.settlement_agent.app import create_app as create_settlement_app
from shopsphere.settlement_agent.settings import SettlementAgentSettings
from shopsphere.support_agent.app import create_app as create_support_app
from shopsphere.support_agent.settings import SupportAgentSettings

AppFactory = Callable[[Any], FastAPI]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("factory", "settings"),
    [
        (create_gateway_app, GatewaySettings()),
        (create_support_app, SupportAgentSettings()),
        (create_settlement_app, SettlementAgentSettings()),
        (create_finance_app, FinanceApprovalSettings()),
        (create_orders_app, OrdersMCPSettings()),
        (create_crm_app, CrmMCPSettings()),
        (create_payments_app, PaymentsMCPSettings()),
        (create_ledger_app, LedgerMCPSettings()),
    ],
)
def test_health_and_readiness(factory: AppFactory, settings: object) -> None:
    app = factory(settings)
    client = TestClient(app)

    health_response = client.get("/healthz")
    ready_response = client.get("/readyz")

    assert health_response.status_code == 200
    assert ready_response.status_code == 200
