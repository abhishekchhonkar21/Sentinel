"""Inventory service — MongoDB-backed stock management."""

from toy_system.inventory_service.infrastructure.container import create_app

app = create_app()
