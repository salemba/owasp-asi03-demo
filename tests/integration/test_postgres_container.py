from __future__ import annotations

import asyncio
import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from testcontainers.postgres import PostgresContainer

from shopsphere.common.config import AppSettings
from shopsphere.common.db import create_engine
from shopsphere.common.seed import deterministic_uuid, run_seed
from shopsphere.mcp_servers.crm.app import create_app as create_crm_app
from shopsphere.mcp_servers.crm.settings import CrmMCPSettings
from shopsphere.mcp_servers.ledger.app import create_app as create_ledger_app
from shopsphere.mcp_servers.ledger.settings import LedgerMCPSettings
from shopsphere.mcp_servers.orders.app import create_app as create_orders_app
from shopsphere.mcp_servers.orders.settings import OrdersMCPSettings
from shopsphere.mcp_servers.payments.app import create_app as create_payments_app
from shopsphere.mcp_servers.payments.settings import PaymentsMCPSettings

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def postgres_env() -> Generator[None, None, None]:
    with PostgresContainer("postgres:16") as postgres:
        os.environ["SHOPSPHERE_DATABASE_HOST"] = postgres.get_container_host_ip()
        os.environ["SHOPSPHERE_DATABASE_PORT"] = str(postgres.get_exposed_port(5432))
        os.environ["SHOPSPHERE_DATABASE_NAME"] = postgres.dbname
        os.environ["SHOPSPHERE_DATABASE_USER"] = postgres.username
        os.environ["SHOPSPHERE_DATABASE_PASSWORD"] = postgres.password
        os.environ["SHOPSPHERE_OPENAI_API_KEY"] = "test-openai"
        os.environ["SHOPSPHERE_ANTHROPIC_API_KEY"] = "test-anthropic"
        os.environ["SHOPSPHERE_TELEMETRY_ENABLED"] = "false"

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

        async def _seed_twice() -> None:
            settings = AppSettings()
            engine = create_engine(settings)
            session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
            await run_seed(session_factory)
            await run_seed(session_factory)
            await engine.dispose()

        asyncio.run(_seed_twice())
        yield


def _auth_headers() -> dict[str, str]:
    return {
        "x-subject": "sam.supervisor",
        "x-roles": "support_supervisor",
        "x-actor-chain": '["sam.supervisor"]',
        "x-tenant": "shopsphere",
    }


def test_seed_idempotent(postgres_env: None) -> None:
    _ = postgres_env
    settings = AppSettings()
    engine = create_engine(settings)

    async def _check_counts() -> tuple[int, int]:
        async with engine.connect() as conn:
            customers = await conn.execute(text("SELECT COUNT(*) FROM crm.customers"))
            orders = await conn.execute(text("SELECT COUNT(*) FROM orders.orders"))
            return int(customers.scalar_one()), int(orders.scalar_one())

    customers_count, orders_count = asyncio.run(_check_counts())
    asyncio.run(engine.dispose())
    assert customers_count == 20
    assert orders_count == 202


def test_orders_tools(postgres_env: None) -> None:
    _ = postgres_env
    client = TestClient(create_orders_app(OrdersMCPSettings()))

    order_id = str(deterministic_uuid("order::bob::95"))
    customer_id = str(deterministic_uuid("customer::bob@shopsphere.test"))

    status_response = client.post(
        "/tools/get_order_status", headers=_auth_headers(), json={"order_id": order_id}
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "DELIVERED_DAMAGED"

    list_response = client.post(
        "/tools/list_customer_orders",
        headers=_auth_headers(),
        json={"customer_id": customer_id},
    )
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 2


def test_crm_tools(postgres_env: None) -> None:
    _ = postgres_env
    client = TestClient(create_crm_app(CrmMCPSettings()))
    customer_id = str(deterministic_uuid("customer::bob@shopsphere.test"))

    customer_response = client.post(
        "/tools/get_customer",
        headers=_auth_headers(),
        json={"customer_id": customer_id},
    )
    assert customer_response.status_code == 200
    assert customer_response.json()["email"] == "bob@shopsphere.test"

    ticket_response = client.post(
        "/tools/create_ticket",
        headers=_auth_headers(),
        json={"customer_id": customer_id, "subject": "integration", "body": "hello"},
    )
    assert ticket_response.status_code == 200
    assert ticket_response.json()["subject"] == "integration"


def test_payments_and_ledger_tools(postgres_env: None) -> None:
    _ = postgres_env
    payments_client = TestClient(create_payments_app(PaymentsMCPSettings()))
    ledger_client = TestClient(create_ledger_app(LedgerMCPSettings()))

    customer_id = str(deterministic_uuid("customer::bob@shopsphere.test"))
    order_id = str(deterministic_uuid("order::bob::95"))
    method_id = str(deterministic_uuid("pm::1::card"))

    refund_response = payments_client.post(
        "/tools/request_refund",
        headers=_auth_headers(),
        json={
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": "20.00",
            "currency": "EUR",
            "reason": "damaged",
            "destination_payment_method_id": method_id,
            "idempotency_key": "integration-key-1",
        },
    )
    assert refund_response.status_code == 200
    refund_id = refund_response.json()["id"]

    ledger_response = ledger_client.post(
        "/tools/post_refund_entry",
        headers=_auth_headers(),
        json={"refund_id": refund_id},
    )
    assert ledger_response.status_code == 200

    balance_response = ledger_client.post(
        "/tools/get_customer_balance",
        headers=_auth_headers(),
        json={"customer_id": customer_id},
    )
    assert balance_response.status_code == 200
