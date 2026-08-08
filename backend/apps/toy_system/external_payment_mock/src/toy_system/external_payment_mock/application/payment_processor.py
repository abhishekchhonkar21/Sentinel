"""Application layer — processes charge requests against the mock provider."""

from __future__ import annotations

import asyncio
import uuid

from toy_system.common.config import ToyServiceSettings
from toy_system.common.fault_state import fault_state_store
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
        fault_state = fault_state_store.get()
        delay_ms = max(self._settings.fault_payment_timeout_ms, fault_state.latency_delay_ms)
        if delay_ms > 0:
            logger.warning("simulating_provider_timeout timeout_ms=%s", delay_ms)
            await asyncio.sleep(delay_ms / 1000)

        if fault_state.reject_charges:
            logger.warning("rejecting_charge order_id=%s", request.order_id)
            return ExternalChargeResponse(
                transaction_id=f"txn_rejected_{request.order_id}",
                status=PaymentStatus.FAILED,
            )

        status = self._policy.evaluate(request)
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"

        logger.info("charge_processed order_id=%s status=%s", request.order_id, status)
        return ExternalChargeResponse(transaction_id=transaction_id, status=status)
