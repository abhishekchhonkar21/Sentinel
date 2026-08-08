"""Simple in-process rate limiter for api-gateway fault injection."""

from __future__ import annotations

import time
from collections import deque

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from toy_system.common.fault_state import fault_state_store
from toy_system.common.logging import configure_logging

logger = configure_logging("api-gateway")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Reject excess traffic with 429 when rate_limit_enabled is set via admin API."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self._timestamps: deque[float] = deque()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        state = fault_state_store.get()
        if not state.rate_limit_enabled or request.url.path.endswith("/health"):
            return await call_next(request)

        now = time.monotonic()
        window = state.rate_limit_window_seconds
        while self._timestamps and self._timestamps[0] <= now - window:
            self._timestamps.popleft()

        if len(self._timestamps) >= state.rate_limit_max_requests:
            logger.warning(
                "rate_limit_exceeded path=%s max=%s window_s=%s",
                request.url.path,
                state.rate_limit_max_requests,
                window,
            )
            return JSONResponse(
                status_code=429,
                content={"code": "rate_limit_exceeded", "message": "Too many requests"},
            )

        self._timestamps.append(now)
        return await call_next(request)
