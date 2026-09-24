from __future__ import annotations

import json

from fastapi import Header
from pydantic import BaseModel, ConfigDict, Field


class CallerContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    roles: list[str] = Field(default_factory=list)
    actor_chain: list[str] = Field(default_factory=list)
    token_claims: dict[str, str] = Field(default_factory=dict)
    tenant: str = "default"


def _parse_actor_chain(header_value: str | None) -> list[str]:
    if not header_value:
        return []
    try:
        parsed = json.loads(header_value)
        if isinstance(parsed, list) and all(isinstance(v, str) for v in parsed):
            return parsed
    except json.JSONDecodeError:
        return []
    return []


def get_caller_context(
    x_subject: str | None = Header(default=None),
    x_roles: str | None = Header(default=None),
    x_actor_chain: str | None = Header(default=None),
    x_tenant: str | None = Header(default=None),
) -> CallerContext:
    roles = [role.strip() for role in x_roles.split(",")] if x_roles else []
    roles = [role for role in roles if role]
    actor_chain = _parse_actor_chain(x_actor_chain)

    return CallerContext(
        subject=x_subject or "anonymous",
        roles=roles,
        actor_chain=actor_chain,
        token_claims={},
        tenant=x_tenant or "default",
    )
