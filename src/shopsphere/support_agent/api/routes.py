from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shopsphere.common.dependencies import get_db_session
from shopsphere.common.health import create_health_router
from shopsphere.common.llm.mock_provider import MockProvider
from shopsphere.common.security import CallerContext, PermissiveAuthorizer, get_caller_context
from shopsphere.support_agent.runner import SupportAgentRunner

router = APIRouter()
router.include_router(create_health_router("support_agent"))


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    ctx: CallerContext = Depends(get_caller_context),
    session: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    runner = SupportAgentRunner(llm_provider=MockProvider(), vuln_profile=True)
    authorizer = PermissiveAuthorizer()
    resp_text = await runner.handle_turn(
        req.message,
        ctx=ctx,
        session=session,
        authorizer=authorizer,
    )
    return ChatResponse(response=resp_text)
