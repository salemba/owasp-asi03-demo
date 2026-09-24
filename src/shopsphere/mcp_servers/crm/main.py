from __future__ import annotations

from shopsphere.mcp_servers.crm.app import create_app
from shopsphere.mcp_servers.crm.settings import CrmMCPSettings

app = create_app(CrmMCPSettings())
