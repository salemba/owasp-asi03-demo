# ADR 0002: Authorization as a Pluggable Port

## Status

Accepted

## Context

Tool servers must consistently enforce authorization while allowing policy evolution from
local placeholders to centralized policy engines.

## Decision

Introduce `Authorizer` as a protocol in `shopsphere.common.security.authz` and route every
MCP tool call through `authorize(ctx, action, resource)` before mutating or disclosing data.

In Step 2, use `AllowAllAuthorizer` for scaffold-only behavior and keep a
`# TODO(step-4)` marker for OPA-backed policy implementation.

## Consequences

- Authorization logic can be swapped without changing tool business handlers.
- Tool invocations become auditable with a standard decision envelope.
- Step 4 can integrate OPA by providing an `Authorizer` implementation only.
