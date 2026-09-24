FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev || uv sync --no-dev

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/Scripts:/app/.venv/bin:${PATH}"

RUN useradd -m appuser
WORKDIR /app

COPY --from=builder /app /app

USER appuser
EXPOSE 8000

CMD ["uvicorn", "shopsphere.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS gateway
CMD ["uvicorn", "shopsphere.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS support-agent
CMD ["uvicorn", "shopsphere.support_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS settlement-agent
CMD ["uvicorn", "shopsphere.settlement_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS finance-approval
CMD ["uvicorn", "shopsphere.finance_approval.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS mcp-orders
CMD ["uvicorn", "shopsphere.mcp_servers.orders.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS mcp-crm
CMD ["uvicorn", "shopsphere.mcp_servers.crm.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS mcp-payments
CMD ["uvicorn", "shopsphere.mcp_servers.payments.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM runtime AS mcp-ledger
CMD ["uvicorn", "shopsphere.mcp_servers.ledger.main:app", "--host", "0.0.0.0", "--port", "8000"]
