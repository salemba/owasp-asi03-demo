from __future__ import annotations

from shopsphere.gateway.app import create_app
from shopsphere.gateway.settings import GatewaySettings

app = create_app(GatewaySettings())
