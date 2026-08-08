"""HTTP adapter — calls toy-service admin APIs to flip runtime fault state."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from fault_injection.infrastructure.settings import FaultInjectionSettings
from sentinel_core.core.exceptions import ExternalServiceError


class ToyServiceClient:
    def __init__(self, *, settings: FaultInjectionSettings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(timeout=settings.http_timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    async def update_fault_state(self, service_name: str, patch: dict[str, Any]) -> datetime:
        base_url = self._settings.service_url(service_name)
        injected_at = datetime.now(UTC)
        try:
            response = await self._client.put(
                f"{base_url}/api/v1/admin/fault-state",
                json=patch,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(service_name, str(exc)) from exc
        return injected_at

    async def clear_fault_state(self, service_name: str) -> None:
        base_url = self._settings.service_url(service_name)
        try:
            response = await self._client.post(f"{base_url}/api/v1/admin/fault-state/clear")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(service_name, str(exc)) from exc

    async def get_fault_state(self, service_name: str) -> dict[str, Any]:
        base_url = self._settings.service_url(service_name)
        try:
            response = await self._client.get(f"{base_url}/api/v1/admin/fault-state")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError(service_name, str(exc)) from exc
        return response.json()
