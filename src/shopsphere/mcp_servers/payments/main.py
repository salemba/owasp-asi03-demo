from __future__ import annotations

from shopsphere.mcp_servers.payments.app import create_app
from shopsphere.mcp_servers.payments.settings import PaymentsMCPSettings

app = create_app(PaymentsMCPSettings())
