from fastapi import APIRouter, Depends

from fault_injection.api.dependencies import get_injection_service
from fault_injection.application.injection_service import FaultInjectionService
from fault_injection.domain.models import InjectFaultRequest, InjectFaultResponse

router = APIRouter(prefix="/api/v1", tags=["fault-injection"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "fault_injection"}


@router.post("/inject-fault", response_model=InjectFaultResponse)
async def inject_fault(
    request: InjectFaultRequest,
    service: FaultInjectionService = Depends(get_injection_service),
) -> InjectFaultResponse:
    return await service.inject(request)
