from __future__ import annotations

from fastapi import APIRouter, FastAPI

from shopsphere.common.config import AppSettings
from shopsphere.common.logging import RequestContextMiddleware, configure_structlog
from shopsphere.common.telemetry import configure_telemetry, instrument_fastapi_app


def create_component_app(settings: AppSettings, *, title: str, router: APIRouter) -> FastAPI:
    configure_structlog(settings.log_level)
    if settings.telemetry_enabled:
        configure_telemetry(settings.service_name, settings.otel_exporter_otlp_endpoint)

    app = FastAPI(title=title)
    app.add_middleware(RequestContextMiddleware)
    app.include_router(router)
    if settings.telemetry_enabled:
        instrument_fastapi_app(app)
    return app
