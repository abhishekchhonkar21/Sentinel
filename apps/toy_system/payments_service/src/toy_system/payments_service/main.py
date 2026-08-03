"""Payments service — processes charges via external payment provider."""

from toy_system.payments_service.infrastructure.container import create_app

app = create_app()
