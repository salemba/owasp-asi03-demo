from __future__ import annotations

from fastapi import FastAPI

from shopsphere.common.app_factory import create_component_app
from shopsphere.gateway.api.routes import router
from shopsphere.gateway.settings import GatewaySettings


def create_app(settings: GatewaySettings) -> FastAPI:
    return create_component_app(settings, title="ShopSphere Gateway", router=router)
