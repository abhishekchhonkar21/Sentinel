from datetime import UTC, datetime

from fault_injection.domain.injectors.registry import InjectorRegistry
from fault_injection.domain.models import InjectFaultRequest, InjectFaultResponse


class FaultInjectionService:
    def __init__(self, *, registry: InjectorRegistry) -> None:
        self._registry = registry

    async def inject(self, request: InjectFaultRequest) -> InjectFaultResponse:
        injector = self._registry.get(request.fault_id)
        injected_at = await injector.inject(request)
        return InjectFaultResponse(
            fault_id=request.fault_id,
            injected_at=injected_at or datetime.now(UTC),
            status="injected",
        )
