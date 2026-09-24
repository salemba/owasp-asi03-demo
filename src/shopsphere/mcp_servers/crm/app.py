from __future__ import annotations

from fastapi import FastAPI

from shopsphere.common.app_factory import create_component_app
from shopsphere.common.runtime import RuntimeContainer
from shopsphere.mcp_servers.crm.api.routes import router
from shopsphere.mcp_servers.crm.mcp_transport import build_mcp_server
from shopsphere.mcp_servers.crm.settings import CrmMCPSettings


def create_app(settings: CrmMCPSettings) -> FastAPI:
    app = create_component_app(settings, title="ShopSphere MCP CRM", router=router)
    app.state.runtime = RuntimeContainer(settings)
    mcp_server = build_mcp_server(app.state.runtime)
    app.mount("/mcp", mcp_server.streamable_http_app(streamable_http_path="/"))
    return app
