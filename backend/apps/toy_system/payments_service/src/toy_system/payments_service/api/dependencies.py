"""Dependency injection for payments-service."""

from functools import lru_cache

from toy_system.payments_service.application.payment_service import PaymentService
from toy_system.payments_service.infrastructure.container import get_external_client
from toy_system.payments_service.infrastructure.settings import get_settings


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService(client=get_external_client(), settings=get_settings())
