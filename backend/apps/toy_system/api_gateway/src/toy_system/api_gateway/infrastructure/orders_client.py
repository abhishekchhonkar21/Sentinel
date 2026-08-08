"""HTTP client adapter — forwards requests to orders-service."""

from __future__ import annotations

import httpx

from sentinel_core.core.exceptions import ExternalServiceError
from toy_system.common.config import ToyServiceSettings
from toy_system.common.http_client import ServiceHttpClient
from toy_system.common.schemas import CreateOrderRequest, CreateOrderResponse


class OrdersClient:
    def __init__(self, *, http: ServiceHttpClient, settings: ToyServiceSettings) -> None:
        self._http = http
        self._base = settings.orders_service_url.rstrip("/")

    async def create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        try:
            response = await self._http.post(
                f"{self._base}/api/v1/orders",
                json=request.model_dump(mode="json"),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("orders-service", str(exc)) from exc
        return CreateOrderResponse.model_validate(response.json())

    async def close(self) -> None:
        await self._http.close()
