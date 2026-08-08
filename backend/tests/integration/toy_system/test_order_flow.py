"""Week 1 integration tests — order flow through all toy-system services in-process."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Ensure toy-system packages are importable in CI without Docker.
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/sentinel_test")
os.environ.setdefault("EXTERNAL_PAYMENT_URL", "http://testserver")
os.environ.setdefault("INVENTORY_SERVICE_URL", "http://testserver")
os.environ.setdefault("PAYMENTS_SERVICE_URL", "http://testserver")
os.environ.setdefault("ORDERS_SERVICE_URL", "http://testserver")


@pytest.fixture
def external_payment_app():
    from toy_system.external_payment_mock.main import app

    return app


@pytest.fixture
def inventory_app():
    from toy_system.common.schemas import InventoryItem
    from toy_system.inventory_service.infrastructure.container import create_app

    # In-memory fake repository for tests without MongoDB.
    class InMemoryInventoryRepository:
        def __init__(self):
            self._items: dict[str, InventoryItem] = {
                "widget-001": InventoryItem(
                    sku="widget-001", name="Basic Widget", quantity=500, price_cents=1999
                ),
            }

        async def find_by_sku(self, sku: str):
            return self._items.get(sku)

        async def reserve_atomic(self, *, sku: str, quantity: int) -> int:
            item = self._items.get(sku)
            if item is None or item.quantity < quantity:
                from toy_system.inventory_service.domain.exceptions import InsufficientStockError

                raise InsufficientStockError(sku, quantity, item.quantity if item else 0)
            updated = item.model_copy(update={"quantity": item.quantity - quantity})
            self._items[sku] = updated
            return updated.quantity

        async def seed_if_empty(self, items):
            pass

    import toy_system.inventory_service.infrastructure.container as container

    container._repository = InMemoryInventoryRepository()
    return create_app()


def test_external_payment_mock_charge(external_payment_app):
    client = TestClient(external_payment_app)
    response = client.post(
        "/api/v1/charge",
        json={"order_id": "ord_test", "amount_cents": 1999, "currency": "USD"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["transaction_id"].startswith("txn_")


def test_inventory_reserve(inventory_app):
    client = TestClient(inventory_app)
    response = client.post(
        "/api/v1/inventory/reserve",
        json={"order_id": "ord_test", "sku": "widget-001", "quantity": 2},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reserved"] == 2
    assert body["remaining"] == 498


def test_api_gateway_health():
    from datetime import UTC, datetime

    import toy_system.api_gateway.infrastructure.container as gw_container
    from toy_system.api_gateway.infrastructure.container import (
        create_app,
        get_settings,
    )
    from toy_system.api_gateway.infrastructure.orders_client import OrdersClient
    from toy_system.common.http_client import ServiceHttpClient
    from toy_system.common.schemas import CreateOrderResponse, OrderStatus

    settings = get_settings()
    gw_container._http_client = ServiceHttpClient(settings)
    gw_container._orders_client = OrdersClient(http=gw_container._http_client, settings=settings)

    # Mock downstream orders-service response.
    mock_response = CreateOrderResponse(
        order_id="ord_mock",
        status=OrderStatus.CONFIRMED,
        total_cents=3998,
        created_at=datetime.now(UTC),
    )

    with patch.object(
        gw_container._orders_client,
        "create_order",
        new=AsyncMock(return_value=mock_response),
    ):
        client = TestClient(create_app())
        health = client.get("/api/v1/health")
        assert health.status_code == 200

        order = client.post(
            "/api/v1/orders",
            json={"customer_id": "cust-1", "items": [{"sku": "widget-001", "quantity": 2}]},
        )
        assert order.status_code == 201
        assert order.json()["status"] == "confirmed"
