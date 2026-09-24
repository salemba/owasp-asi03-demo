from __future__ import annotations

from shopsphere.common.config import AppSettings


class PaymentsMCPSettings(AppSettings):
    service_name: str = "mcp_payments"
