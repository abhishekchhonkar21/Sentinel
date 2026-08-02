"""Application layer — processes charge requests against the mock provider."""

from __future__ import annotations

import asyncio
import uuid

from toy_system.common.config import ToyServiceSettings
from toy_system.common.logging import configure_logging
from toy_system.common.schemas import ExternalChargeRequest, ExternalChargeResponse, PaymentStatus
from toy_system.external_payment_mock.domain.charge_policy import ChargePolicy

logger = configure_logging("external-payment-mock")


class ExternalPaymentProcessor:
    """Use case: accept a charge request and return a provider-style response."""

    def __init__(self, *, settings: ToyServiceSettings) -> None:
        self._settings = settings
        self._policy = ChargePolicy()

    async def charge(self, request: ExternalChargeRequest) -> ExternalChargeResponse:
        # Simulate provider latency — fault injection raises this value (Week 2).
        if self._settings.fault_payment_timeout_ms > 0:
            logger.warning(
                "simulating_provider_timeout timeout_ms=%s",
                self._settings.fault_payment_timeout_ms,
            )
            await asyncio.sleep(self._settings.fault_payment_timeout_ms / 1000)

        status = self._policy.evaluate(request)
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"

        logger.info("charge_processed order_id=%s status=%s", request.order_id, status)
        return ExternalChargeResponse(transaction_id=transaction_id, status=status)
