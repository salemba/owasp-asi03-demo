from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.a2a import A2AMessage
from shopsphere.common.dependencies import get_db_session
from shopsphere.common.health import create_health_router
from shopsphere.common.llm.mock_provider import MockProvider
from shopsphere.common.security import CallerContext, PermissiveAuthorizer, get_caller_context
from shopsphere.settlement_agent.runner import SettlementAgentRunner

router = APIRouter()
router.include_router(create_health_router("settlement_agent"))


@router.post("/a2a/settlement")
async def process_a2a_settlement(
    message: A2AMessage,
    ctx: CallerContext = Depends(get_caller_context),
    session: AsyncSession = Depends(get_db_session),
) -> str:
    runner = SettlementAgentRunner(llm_provider=MockProvider(), vuln_profile=True)
    authorizer = PermissiveAuthorizer()
    return await runner.process_a2a_request(
        message,
        ctx=ctx,
        session=session,
        authorizer=authorizer,
    )
