from __future__ import annotations

from fastapi import FastAPI

from shopsphere.common.app_factory import create_component_app
from shopsphere.support_agent.api.routes import router
from shopsphere.support_agent.settings import SupportAgentSettings


def create_app(settings: SupportAgentSettings) -> FastAPI:
    return create_component_app(settings, title="ShopSphere Support Agent", router=router)
