from __future__ import annotations

from shopsphere.mcp_servers.ledger.app import create_app
from shopsphere.mcp_servers.ledger.settings import LedgerMCPSettings

app = create_app(LedgerMCPSettings())
