"""Registry — maps fault_id from fault_catalogue to concrete injector."""

from fault_injection.domain.injectors.base import FaultInjector
from sentinel_core.core.exceptions import NotFoundError


class InjectorRegistry:
    def __init__(self) -> None:
        self._injectors: dict[str, FaultInjector] = {}

    def register(self, injector: FaultInjector) -> None:
        self._injectors[injector.fault_id] = injector

    def get(self, fault_id: str) -> FaultInjector:
        if fault_id not in self._injectors:
            raise NotFoundError("fault_injector", fault_id)
        return self._injectors[fault_id]
