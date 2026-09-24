from __future__ import annotations

from shopsphere.mcp_servers.orders.app import create_app
from shopsphere.mcp_servers.orders.settings import OrdersMCPSettings

app = create_app(OrdersMCPSettings())
