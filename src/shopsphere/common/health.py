from __future__ import annotations

from fastapi import APIRouter


def create_health_router(component: str) -> APIRouter:
    router = APIRouter()

    @router.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "component": component}

    @router.get("/readyz")
    async def readyz() -> dict[str, str]:
        # TODO(step-N): Add component dependency checks.
        return {"status": "ready", "component": component}

    return router
