"""Dependency injection for external-payment-mock."""

from functools import lru_cache

from toy_system.external_payment_mock.application.payment_processor import ExternalPaymentProcessor
from toy_system.external_payment_mock.infrastructure.settings import get_settings


@lru_cache
def get_payment_processor() -> ExternalPaymentProcessor:
    return ExternalPaymentProcessor(settings=get_settings())
