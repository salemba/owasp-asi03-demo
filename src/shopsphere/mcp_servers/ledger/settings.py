from __future__ import annotations

from shopsphere.common.config import AppSettings


class LedgerMCPSettings(AppSettings):
    service_name: str = "mcp_ledger"
