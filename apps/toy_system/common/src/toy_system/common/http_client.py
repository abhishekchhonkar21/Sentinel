"""Async HTTP client base — forwards trace_id to downstream services."""

from __future__ import annotations

from typing import Any

import httpx

from toy_system.common.config import ToyServiceSettings
from toy_system.common.logging import trace_id_var


class ServiceHttpClient:
    """Thin wrapper around httpx.AsyncClient with trace propagation.

    Subclass or compose this in each service's infrastructure layer rather than
    calling httpx directly — keeps timeouts and headers consistent.
    """

    def __init__(self, settings: ToyServiceSettings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(timeout=settings.http_timeout_seconds)

    async def close(self) -> None:
        await self._client.aclose()

    def _headers(self) -> dict[str, str]:
        return {"X-Trace-Id": trace_id_var.get(), "Content-Type": "application/json"}

    async def post(self, url: str, *, json: dict[str, Any]) -> httpx.Response:
        return await self._client.post(url, json=json, headers=self._headers())

    async def get(self, url: str) -> httpx.Response:
        return await self._client.get(url, headers=self._headers())
