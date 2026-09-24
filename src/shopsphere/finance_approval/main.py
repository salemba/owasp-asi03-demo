from __future__ import annotations

from shopsphere.finance_approval.app import create_app
from shopsphere.finance_approval.settings import FinanceApprovalSettings

app = create_app(FinanceApprovalSettings())
