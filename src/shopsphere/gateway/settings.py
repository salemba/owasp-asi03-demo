from __future__ import annotations

from shopsphere.common.config import AppSettings


class GatewaySettings(AppSettings):
    service_name: str = "gateway"
    gateway_support_agent_url: str
    keycloak_issuer_url: str
    keycloak_client_id: str
    keycloak_client_secret: str
