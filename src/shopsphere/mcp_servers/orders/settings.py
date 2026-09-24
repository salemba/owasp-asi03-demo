from __future__ import annotations

from shopsphere.common.config import AppSettings


class OrdersMCPSettings(AppSettings):
    service_name: str = "mcp_orders"
