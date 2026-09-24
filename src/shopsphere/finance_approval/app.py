from __future__ import annotations

from fastapi import FastAPI

from shopsphere.common.app_factory import create_component_app
from shopsphere.finance_approval.api.routes import router
from shopsphere.finance_approval.settings import FinanceApprovalSettings


def create_app(settings: FinanceApprovalSettings) -> FastAPI:
    return create_component_app(settings, title="ShopSphere Finance Approval", router=router)
