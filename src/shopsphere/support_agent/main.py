from __future__ import annotations

from shopsphere.support_agent.app import create_app
from shopsphere.support_agent.settings import SupportAgentSettings

app = create_app(SupportAgentSettings())
