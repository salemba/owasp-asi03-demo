from __future__ import annotations

from fastapi import FastAPI

from shopsphere.common.app_factory import create_component_app
from shopsphere.common.runtime import RuntimeContainer
from shopsphere.mcp_servers.ledger.api.routes import router
from shopsphere.mcp_servers.ledger.mcp_transport import build_mcp_server
from shopsphere.mcp_servers.ledger.settings import LedgerMCPSettings


def create_app(settings: LedgerMCPSettings) -> FastAPI:
    app = create_component_app(settings, title="ShopSphere MCP Ledger", router=router)
    app.state.runtime = RuntimeContainer(settings)
    mcp_server = build_mcp_server(app.state.runtime)
    app.mount("/mcp", mcp_server.streamable_http_app(streamable_http_path="/"))
    return app
