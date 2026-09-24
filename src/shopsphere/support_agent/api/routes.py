from __future__ import annotations

from fastapi import APIRouter

from shopsphere.common.health import create_health_router

router = APIRouter()
router.include_router(create_health_router("support_agent"))
