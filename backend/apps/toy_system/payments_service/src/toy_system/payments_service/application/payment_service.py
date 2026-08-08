"""Application layer — charge orchestration."""

from __future__ import annotations

import uuid

from toy_system.common.config import ToyServiceSettings
from toy_system.common.fault_state import fault_state_store
from toy_system.common.logging import configure_logging
from toy_system.common.schemas import (
    ChargePaymentRequest,
    ChargePaymentResponse,
    ExternalChargeRequest,
)
from toy_system.payments_service.infrastructure.external_payment_client import ExternalPaymentClient

logger = configure_logging("payments-service")


class PaymentService:
    """Use case: validate charge request and delegate to external provider.

    Contains a deliberate fault-prone code path (null-deref simulation) that
    Week 2 fault injection can enable via FAULT_NULL_DEREF=true.
    """

    def __init__(self, *, client: ExternalPaymentClient, settings: ToyServiceSettings) -> None:
        self._client = client
        self._settings = settings

    async def charge(self, request: ChargePaymentRequest) -> ChargePaymentResponse:
        logger.info(
            "charging_payment order_id=%s amount_cents=%s",
            request.order_id,
            request.amount_cents,
        )

        # Fault-prone path: simulates a bad deploy that crashes before charging.
        # Enabled via env (boot) or runtime admin API (Week 2 fault injection).
        fault_state = fault_state_store.get()
        if self._settings.fault_null_deref or fault_state.null_deref:
            logger.error("fault_null_deref_triggered order_id=%s", request.order_id)
            raise RuntimeError("Simulated null-deref fault from bad deploy")

        external_request = ExternalChargeRequest(
            order_id=request.order_id,
            amount_cents=request.amount_cents,
            currency=request.currency,
        )
        provider_response = await self._client.charge(external_request)

        payment_id = f"pay_{uuid.uuid4().hex[:12]}"
        status = provider_response.status

        logger.info(
            "payment_completed payment_id=%s order_id=%s status=%s",
            payment_id,
            request.order_id,
            status,
        )
        return ChargePaymentResponse(
            payment_id=payment_id,
            order_id=request.order_id,
            status=status,
            amount_cents=request.amount_cents,
        )
