"""Application layer — order placement saga (reserve → pay → confirm)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from toy_system.common.config import ToyServiceSettings
from toy_system.common.logging import configure_logging
from toy_system.common.schemas import (
    ChargePaymentRequest,
    CreateOrderRequest,
    CreateOrderResponse,
    OrderStatus,
    PaymentStatus,
    ReserveStockRequest,
)
from toy_system.orders_service.domain.order_pricing import OrderPricing
from toy_system.orders_service.infrastructure.downstream_clients import (
    InventoryClient,
    PaymentsClient,
)

logger = configure_logging("orders-service")


class OrderService:
    """Orchestrates the happy-path order flow across inventory and payments.

    Week 1: sequential reserve-then-charge (no distributed transaction).
    If payment fails after reservation, stock is not rolled back — acceptable
  for the toy system; Week 2 may add compensating actions.
    """

    def __init__(
        self,
        *,
        inventory_client: InventoryClient,
        payments_client: PaymentsClient,
        settings: ToyServiceSettings,
    ) -> None:
        self._inventory = inventory_client
        self._payments = payments_client
        self._settings = settings
        self._pricing = OrderPricing()

    async def place_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        logger.info("placing_order order_id=%s customer_id=%s", order_id, request.customer_id)

        # Step 1: Look up prices and compute total.
        total_cents = 0
        for item in request.items:
            catalog_item = await self._inventory.get_item(item.sku)
            total_cents += self._pricing.line_total(catalog_item.price_cents, item.quantity)

        # Step 2: Reserve stock for each line item.
        for item in request.items:
            await self._inventory.reserve_stock(
                ReserveStockRequest(order_id=order_id, sku=item.sku, quantity=item.quantity)
            )

        # Step 3: Charge the customer.
        payment = await self._payments.charge(
            ChargePaymentRequest(
                order_id=order_id,
                amount_cents=total_cents,
            )
        )

        status = (
            OrderStatus.CONFIRMED
            if payment.status == PaymentStatus.SUCCEEDED
            else OrderStatus.FAILED
        )

        logger.info("order_completed order_id=%s status=%s total_cents=%s", order_id, status, total_cents)
        return CreateOrderResponse(
            order_id=order_id,
            status=status,
            total_cents=total_cents,
            created_at=datetime.now(UTC),
        )
