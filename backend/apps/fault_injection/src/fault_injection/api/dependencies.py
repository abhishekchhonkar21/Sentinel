from functools import lru_cache

from fault_injection.application.injection_service import FaultInjectionService
from fault_injection.domain.injectors.registry import InjectorRegistry


@lru_cache
def get_injection_service() -> FaultInjectionService:
    return FaultInjectionService(registry=InjectorRegistry())
