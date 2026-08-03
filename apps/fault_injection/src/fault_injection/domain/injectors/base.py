"""Strategy pattern — each fault type implements FaultInjector."""

from abc import ABC, abstractmethod
from datetime import datetime

from fault_injection.domain.models import InjectFaultRequest


class FaultInjector(ABC):
    fault_id: str

    @abstractmethod
    async def inject(self, request: InjectFaultRequest) -> datetime:
        """Trigger fault and return exact injection timestamp."""
