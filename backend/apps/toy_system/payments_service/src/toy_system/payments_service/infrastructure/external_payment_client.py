"""HTTP client adapter — calls external-payment-mock over the network."""

from __future__ import annotations

import httpx

from sentinel_core.core.exceptions import ExternalServiceError
from toy_system.common.config import ToyServiceSettings
from toy_system.common.http_client import ServiceHttpClient
from toy_system.common.schemas import ExternalChargeRequest, ExternalChargeResponse


class ExternalPaymentClient:
    """Adapter implementing the outbound port to the external payment provider."""

    def __init__(self, *, http: ServiceHttpClient, settings: ToyServiceSettings) -> None:
        self._http = http
        self._settings = settings

    async def charge(self, request: ExternalChargeRequest) -> ExternalChargeResponse:
        url = f"{self._settings.external_payment_url.rstrip('/')}/api/v1/charge"
        try:
            response = await self._http.post(url, json=request.model_dump(mode="json"))
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ExternalServiceError("external-payment-mock", str(exc)) from exc
        return ExternalChargeResponse.model_validate(response.json())

    async def close(self) -> None:
        await self._http.close()
