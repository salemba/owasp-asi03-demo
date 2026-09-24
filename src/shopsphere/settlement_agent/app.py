from __future__ import annotations

from fastapi import FastAPI

from shopsphere.common.app_factory import create_component_app
from shopsphere.settlement_agent.api.routes import router
from shopsphere.settlement_agent.settings import SettlementAgentSettings


def create_app(settings: SettlementAgentSettings) -> FastAPI:
    return create_component_app(settings, title="ShopSphere Settlement Agent", router=router)
