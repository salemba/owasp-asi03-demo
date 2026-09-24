from __future__ import annotations

from decimal import Decimal
from typing import cast
from uuid import UUID, uuid4

import pytest

from shopsphere.common.persistence.models import (
    OrderORM,
    OrderStatus,
    PaymentMethodORM,
    PaymentMethodType,
    RefundORM,
    RefundStatus,
)
from shopsphere.mcp_servers.orders.domain.ports import OrdersRepository
from shopsphere.mcp_servers.payments.domain.ports import PaymentsRepository


class FakeOrdersRepository:
    def __init__(self, order: OrderORM) -> None:
        self._order = order

    async def get_order(self, order_id: UUID) -> OrderORM | None:
        return self._order if self._order.id == order_id else None

    async def list_customer_orders(self, customer_id: UUID) -> list[OrderORM]:
        return [self._order] if self._order.customer_id == customer_id else []

    async def get_order_status(self, order_id: UUID) -> OrderStatus | None:
        order = await self.get_order(order_id)
        return order.status if order else None


class FakePaymentsRepository:
    def __init__(self, payment_method: PaymentMethodORM, refund: RefundORM) -> None:
        self._payment_method = payment_method
        self._refund = refund

    async def request_refund(
        self,
        *,
        order_id: UUID,
        customer_id: UUID,
        amount: str,
        currency: str,
        destination_payment_method_id: UUID,
        idempotency_key: str,
        requested_by: str,
    ) -> RefundORM:
        _ = (
            order_id,
            customer_id,
            amount,
            currency,
            destination_payment_method_id,
            idempotency_key,
            requested_by,
        )
        return self._refund

    async def list_payment_methods(self, customer_id: UUID) -> list[PaymentMethodORM]:
        return [self._payment_method] if self._payment_method.customer_id == customer_id else []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_orders_protocol_with_fake() -> None:
    customer_id = uuid4()
    order_id = uuid4()
    order = OrderORM(
        id=order_id,
        customer_id=customer_id,
        status=OrderStatus.DELIVERED,
        total=Decimal("10.00"),
        currency="EUR",
    )
    repository = cast(OrdersRepository, FakeOrdersRepository(order))
    assert await repository.get_order(order_id) is not None
    assert await repository.get_order_status(order_id) == OrderStatus.DELIVERED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_payments_protocol_with_fake() -> None:
    customer_id = uuid4()
    payment_method = PaymentMethodORM(
        id=uuid4(),
        customer_id=customer_id,
        type=PaymentMethodType.CARD,
        masked_ref="****",
        is_active=True,
    )
    refund = RefundORM(
        id=uuid4(),
        order_id=uuid4(),
        customer_id=customer_id,
        amount=Decimal("10.00"),
        currency="EUR",
        destination_payment_method_id=payment_method.id,
        status=RefundStatus.PENDING,
        idempotency_key="k1",
        requested_by="tester",
    )
    repository = cast(PaymentsRepository, FakePaymentsRepository(payment_method, refund))
    methods = await repository.list_payment_methods(customer_id)
    assert len(methods) == 1
