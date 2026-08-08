"""HTTP routes for payment processing."""

from fastapi import APIRouter, Depends

from toy_system.common.schemas import ChargePaymentRequest, ChargePaymentResponse
from toy_system.payments_service.api.dependencies import get_payment_service
from toy_system.payments_service.application.payment_service import PaymentService

router = APIRouter(prefix="/api/v1", tags=["payments"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "payments-service"}


@router.post("/payments/charge", response_model=ChargePaymentResponse)
async def charge_payment(
    request: ChargePaymentRequest,
    service: PaymentService = Depends(get_payment_service),
) -> ChargePaymentResponse:
    return await service.charge(request)
