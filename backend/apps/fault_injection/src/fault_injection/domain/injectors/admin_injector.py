"""Admin API fault injector — sets runtime fault state on a target service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fault_injection.adapters.toy_service_client import ToyServiceClient
from fault_injection.domain.injectors.base import FaultInjector
from fault_injection.domain.models import InjectFaultRequest


class AdminFaultInjector(FaultInjector):
    """Strategy implementation — PATCH fault state via toy-service admin API."""

    def __init__(
        self,
        *,
        fault_id: str,
        service_name: str,
        default_state: dict[str, Any],
        client: ToyServiceClient,
    ) -> None:
        self.fault_id = fault_id
        self._service_name = service_name
        self._default_state = default_state
        self._client = client

    async def inject(self, request: InjectFaultRequest) -> datetime:
        state = {**self._default_state, **request.params}
        return await self._client.update_fault_state(self._service_name, state)

    async def clear(self) -> datetime:
        await self._client.clear_fault_state(self._service_name)
        return datetime.now(UTC)
