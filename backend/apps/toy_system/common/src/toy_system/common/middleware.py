"""HTTP middleware — trace ID propagation and request latency measurement."""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from toy_system.common.logging import configure_logging, trace_id_var


class TraceIdMiddleware(BaseHTTPMiddleware):
    """Assign or forward X-Trace-Id and log every request with latency_ms."""

    def __init__(self, app, service_name: str) -> None:
        super().__init__(app)
        self._logger = configure_logging(service_name)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
        token = trace_id_var.set(trace_id)
        started = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000
            self._logger.exception(
                "request_failed",
                extra={"latency_ms": round(elapsed_ms, 2)},
            )
            raise
        else:
            elapsed_ms = (time.perf_counter() - started) * 1000
            self._logger.info(
                "%s %s -> %s",
                request.method,
                request.url.path,
                response.status_code,
                extra={"latency_ms": round(elapsed_ms, 2)},
            )
            response.headers["X-Trace-Id"] = trace_id
            return response
        finally:
            trace_id_var.reset(token)
