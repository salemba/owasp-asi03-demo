from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid5

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from shopsphere.common.config import AppSettings
from shopsphere.common.db import create_engine
from shopsphere.common.persistence.models import (
    CRMSupportTicketORM,
    CustomerORM,
    CustomerTier,
    JournalEntryORM,
    LedgerAccountORM,
    LedgerSide,
    OrderLineORM,
    OrderORM,
    OrderStatus,
    PaymentMethodORM,
    PaymentMethodType,
    PostingORM,
)

NAMESPACE = UUID("11111111-2222-3333-4444-555555555555")


@dataclass(frozen=True)
class Persona:
    email: str
    full_name: str
    tier: CustomerTier


def deterministic_uuid(label: str) -> UUID:
    return uuid5(NAMESPACE, label)


SessionFactory = async_sessionmaker[AsyncSession]


async def seed_customers_and_tickets(now: datetime, session_factory: SessionFactory) -> list[UUID]:
    personas = [
        Persona("alice@shopsphere.test", "Alice Attacker", CustomerTier.SILVER),
        Persona("bob@shopsphere.test", "Bob Victim", CustomerTier.GOLD),
    ]
    personas.extend(
        Persona(
            email=f"customer{i}@shopsphere.test",
            full_name=f"Customer {i}",
            tier=[
                CustomerTier.BRONZE,
                CustomerTier.SILVER,
                CustomerTier.GOLD,
                CustomerTier.PLATINUM,
            ][i % 4],
        )
        for i in range(1, 19)
    )

    customer_rows: list[dict[str, object]] = [
        {
            "id": deterministic_uuid(f"customer::{persona.email}"),
            "email": persona.email,
            "full_name": persona.full_name,
            "tier": persona.tier,
            "created_at": now - timedelta(days=200),
        }
        for persona in personas
    ]

    ticket_rows: list[dict[str, object]] = [
        {
            "id": deterministic_uuid(f"ticket::{persona.email}"),
            "customer_id": deterministic_uuid(f"customer::{persona.email}"),
            "subject": "Welcome ticket",
            "body": "Seeded onboarding support ticket.",
            "created_at": now - timedelta(days=30),
        }
        for persona in personas[:4]
    ]

    async with session_factory() as session:
        await session.execute(
            insert(CustomerORM).values(customer_rows).on_conflict_do_nothing(index_elements=["id"])
        )
        await session.execute(
            insert(CRMSupportTicketORM)
            .values(ticket_rows)
            .on_conflict_do_nothing(index_elements=["id"])
        )
        await session.commit()

    return [deterministic_uuid(f"customer::{persona.email}") for persona in personas]


def build_order_rows(
    customer_ids: list[UUID], now: datetime
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rng = random.Random(42)  # noqa: S311
    statuses = [
        OrderStatus.PLACED,
        OrderStatus.SHIPPED,
        OrderStatus.DELIVERED,
        OrderStatus.DELIVERED_DAMAGED,
        OrderStatus.LOST,
        OrderStatus.RETURNED,
    ]

    order_rows: list[dict[str, object]] = []
    line_rows: list[dict[str, object]] = []

    for index in range(200):
        customer_id = customer_ids[index % len(customer_ids)]
        status = statuses[rng.randrange(0, len(statuses))]
        placed_at = now - timedelta(days=rng.randrange(1, 180), hours=rng.randrange(0, 23))
        delivered_at = (
            placed_at + timedelta(days=rng.randrange(2, 12))
            if status
            in {
                OrderStatus.DELIVERED,
                OrderStatus.DELIVERED_DAMAGED,
                OrderStatus.RETURNED,
                OrderStatus.LOST,
            }
            else None
        )
        total = Decimal(str(rng.randrange(15, 550)))

        order_id = deterministic_uuid(f"order::{index}")
        order_rows.append(
            {
                "id": order_id,
                "customer_id": customer_id,
                "status": status,
                "total": total,
                "currency": "EUR",
                "placed_at": placed_at,
                "delivered_at": delivered_at,
            }
        )

        line_rows.append(
            {
                "id": deterministic_uuid(f"order_line::{index}"),
                "order_id": order_id,
                "sku": f"SKU-{1000 + index}",
                "quantity": 1,
                "unit_price": total,
                "currency": "EUR",
            }
        )

    bob_id = deterministic_uuid("customer::bob@shopsphere.test")
    special_orders = [
        {
            "id": deterministic_uuid("order::bob::480"),
            "customer_id": bob_id,
            "status": OrderStatus.DELIVERED,
            "total": Decimal("480.00"),
            "currency": "EUR",
            "placed_at": now - timedelta(days=21),
            "delivered_at": now - timedelta(days=15),
        },
        {
            "id": deterministic_uuid("order::bob::95"),
            "customer_id": bob_id,
            "status": OrderStatus.DELIVERED_DAMAGED,
            "total": Decimal("95.00"),
            "currency": "EUR",
            "placed_at": now - timedelta(days=12),
            "delivered_at": now - timedelta(days=5),
        },
    ]
    special_lines = [
        {
            "id": deterministic_uuid("order_line::bob::480"),
            "order_id": special_orders[0]["id"],
            "sku": "SKU-BOB-480",
            "quantity": 1,
            "unit_price": Decimal("480.00"),
            "currency": "EUR",
        },
        {
            "id": deterministic_uuid("order_line::bob::95"),
            "order_id": special_orders[1]["id"],
            "sku": "SKU-BOB-095",
            "quantity": 1,
            "unit_price": Decimal("95.00"),
            "currency": "EUR",
        },
    ]

    order_rows.extend(special_orders)
    line_rows.extend(special_lines)
    return order_rows, line_rows


async def seed_orders(
    customer_ids: list[UUID], now: datetime, session_factory: SessionFactory
) -> None:
    orders, lines = build_order_rows(customer_ids, now)
    async with session_factory() as session:
        await session.execute(
            insert(OrderORM).values(orders).on_conflict_do_nothing(index_elements=["id"])
        )
        await session.execute(
            insert(OrderLineORM).values(lines).on_conflict_do_nothing(index_elements=["id"])
        )
        await session.commit()


async def seed_payment_methods(customer_ids: list[UUID], session_factory: SessionFactory) -> None:
    methods: list[dict[str, object]] = []
    for index, customer_id in enumerate(customer_ids):
        methods.append(
            {
                "id": deterministic_uuid(f"pm::{index}::card"),
                "customer_id": customer_id,
                "type": PaymentMethodType.CARD,
                "masked_ref": f"**** **** **** {1000 + index:04d}",
                "is_active": True,
            }
        )
        methods.append(
            {
                "id": deterministic_uuid(f"pm::{index}::wallet"),
                "customer_id": customer_id,
                "type": PaymentMethodType.WALLET,
                "masked_ref": f"wallet-{index:03d}",
                "is_active": True,
            }
        )

    async with session_factory() as session:
        await session.execute(
            insert(PaymentMethodORM).values(methods).on_conflict_do_nothing(index_elements=["id"])
        )
        await session.commit()


async def seed_ledger(
    customer_ids: list[UUID], now: datetime, session_factory: SessionFactory
) -> None:
    accounts = [
        {
            "id": deterministic_uuid("ledger_account::cash"),
            "code": "CASH",
            "name": "Cash",
            "currency": "EUR",
        },
        {
            "id": deterministic_uuid("ledger_account::refund_liability"),
            "code": "REFUND_LIABILITY",
            "name": "Refund Liability",
            "currency": "EUR",
        },
    ]

    async with session_factory() as session:
        await session.execute(
            insert(LedgerAccountORM).values(accounts).on_conflict_do_nothing(index_elements=["id"])
        )

        journal_id = deterministic_uuid("journal::opening")
        await session.execute(
            insert(JournalEntryORM)
            .values(
                {
                    "id": journal_id,
                    "reference_id": deterministic_uuid("journal_ref::opening"),
                    "description": "Opening balances",
                    "created_at": now - timedelta(days=200),
                }
            )
            .on_conflict_do_nothing(index_elements=["id"])
        )

        opening_amount = Decimal("10000.00")
        postings = [
            {
                "id": deterministic_uuid("posting::opening::debit"),
                "entry_id": journal_id,
                "account_id": deterministic_uuid("ledger_account::cash"),
                "customer_id": customer_ids[0],
                "side": LedgerSide.DEBIT,
                "amount": opening_amount,
                "currency": "EUR",
                "created_at": now - timedelta(days=200),
            },
            {
                "id": deterministic_uuid("posting::opening::credit"),
                "entry_id": journal_id,
                "account_id": deterministic_uuid("ledger_account::refund_liability"),
                "customer_id": customer_ids[0],
                "side": LedgerSide.CREDIT,
                "amount": opening_amount,
                "currency": "EUR",
                "created_at": now - timedelta(days=200),
            },
        ]
        await session.execute(
            insert(PostingORM).values(postings).on_conflict_do_nothing(index_elements=["id"])
        )
        await session.commit()


async def run_seed(session_factory: SessionFactory) -> None:
    now = datetime.now(UTC)
    customer_ids = await seed_customers_and_tickets(now, session_factory)
    await seed_orders(customer_ids, now, session_factory)
    await seed_payment_methods(customer_ids, session_factory)
    await seed_ledger(customer_ids, now, session_factory)


if __name__ == "__main__":
    settings = AppSettings()
    engine = create_engine(settings)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    asyncio.run(run_seed(session_factory))
