from fastapi import APIRouter, Depends

from fault_injection.api.dependencies import get_injection_service
from fault_injection.application.injection_service import FaultInjectionService
from fault_injection.domain.models import (
    ClearFaultRequest,
    ClearFaultResponse,
    InjectFaultRequest,
    InjectFaultResponse,
    SystemStatusResponse,
)
from sentinel_core.schemas.contracts import FaultCatalogueEntry

router = APIRouter(prefix="/api/v1", tags=["fault-injection"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "fault_injection"}


@router.get("/faults", response_model=list[FaultCatalogueEntry])
async def list_faults(
    service: FaultInjectionService = Depends(get_injection_service),
) -> list[FaultCatalogueEntry]:
    return await service.list_faults()


@router.get("/system-status", response_model=SystemStatusResponse)
async def system_status(
    service: FaultInjectionService = Depends(get_injection_service),
) -> SystemStatusResponse:
    return await service.get_system_status()


@router.post("/inject-fault", response_model=InjectFaultResponse)
async def inject_fault(
    request: InjectFaultRequest,
    service: FaultInjectionService = Depends(get_injection_service),
) -> InjectFaultResponse:
    return await service.inject(request)


@router.post("/clear-fault", response_model=ClearFaultResponse)
async def clear_fault(
    request: ClearFaultRequest,
    service: FaultInjectionService = Depends(get_injection_service),
) -> ClearFaultResponse:
    return await service.clear_fault(request.service)
