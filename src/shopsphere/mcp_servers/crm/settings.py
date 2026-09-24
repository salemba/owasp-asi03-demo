from __future__ import annotations

from shopsphere.common.config import AppSettings


class CrmMCPSettings(AppSettings):
    service_name: str = "mcp_crm"
