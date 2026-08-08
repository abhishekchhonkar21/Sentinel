"""Dependency injection for orders-service."""

from functools import lru_cache

from toy_system.orders_service.application.order_service import OrderService
from toy_system.orders_service.infrastructure.container import get_clients
from toy_system.orders_service.infrastructure.settings import get_settings


@lru_cache
def get_order_service() -> OrderService:
    inventory_client, payments_client = get_clients()
    return OrderService(
        inventory_client=inventory_client,
        payments_client=payments_client,
        settings=get_settings(),
    )
