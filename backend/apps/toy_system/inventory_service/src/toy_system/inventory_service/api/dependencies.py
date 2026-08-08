"""Dependency injection for inventory-service."""

from functools import lru_cache

from toy_system.inventory_service.application.inventory_service import InventoryService
from toy_system.inventory_service.infrastructure.container import get_repository
from toy_system.inventory_service.infrastructure.settings import get_settings


@lru_cache
def get_inventory_service() -> InventoryService:
    return InventoryService(repository=get_repository(), settings=get_settings())
