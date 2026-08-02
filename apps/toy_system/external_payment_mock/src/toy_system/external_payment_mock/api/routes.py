"""HTTP routes for the external payment provider mock."""

from fastapi import APIRouter, Depends

from toy_system.common.schemas import ExternalChargeRequest, ExternalChargeResponse
from toy_system.external_payment_mock.api.dependencies import get_payment_processor
from toy_system.external_payment_mock.application.payment_processor import ExternalPaymentProcessor

router = APIRouter(prefix="/api/v1", tags=["external-payment"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "external-payment-mock"}


@router.post("/charge", response_model=ExternalChargeResponse)
async def charge(
    request: ExternalChargeRequest,
    processor: ExternalPaymentProcessor = Depends(get_payment_processor),
) -> ExternalChargeResponse:
    """Simulate a third-party card charge — the leaf node of the payment chain."""
    return await processor.charge(request)
