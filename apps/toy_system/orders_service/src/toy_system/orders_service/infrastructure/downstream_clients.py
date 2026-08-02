"""HTTP client adapters for downstream toy-system services."""

from __future__ import annotations

import httpx

from sentinel_core.core.exceptions import ExternalServiceError
from toy_system.common.config import ToyServiceSettings
from toy_system.common.http_client import ServiceHttpClient
from toy_system.common.schemas import (
    ChargePaymentRequest,
    ChargePaymentResponse,
    InventoryItem,
    ReserveStockRequest,
    ReserveStockResponse,
)


class InventoryClient:
    """Outbound port to inventory-service."""

    def __init__(self, *, http: ServiceHttpClient, settings: ToyServiceSettings) -> None:
        self._http = http
        self._base = settings.inventory_service_url.rstrip("/")

    async def get_item(self, sku: str) -> InventoryItem:
        try:
            response = await self._http.get(f"{self._base}/api/v1/inventory/{sku}")
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("inventory-service", str(exc)) from exc
        return InventoryItem.model_validate(response.json())

    async def reserve_stock(self, request: ReserveStockRequest) -> ReserveStockResponse:
        try:
            response = await self._http.post(
                f"{self._base}/api/v1/inventory/reserve",
                json=request.model_dump(mode="json"),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("inventory-service", str(exc)) from exc
        return ReserveStockResponse.model_validate(response.json())


class PaymentsClient:
    """Outbound port to payments-service."""

    def __init__(self, *, http: ServiceHttpClient, settings: ToyServiceSettings) -> None:
        self._http = http
        self._base = settings.payments_service_url.rstrip("/")

    async def charge(self, request: ChargePaymentRequest) -> ChargePaymentResponse:
        try:
            response = await self._http.post(
                f"{self._base}/api/v1/payments/charge",
                json=request.model_dump(mode="json"),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("payments-service", str(exc)) from exc
        return ChargePaymentResponse.model_validate(response.json())
