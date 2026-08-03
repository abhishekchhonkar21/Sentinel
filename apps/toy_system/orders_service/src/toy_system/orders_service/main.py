"""Orders service — orchestrates inventory reservation and payment."""

from toy_system.orders_service.infrastructure.container import create_app

app = create_app()
