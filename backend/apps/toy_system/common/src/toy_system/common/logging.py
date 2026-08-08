"""Structured JSON logging — Week 3 will scrape these from stdout."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# Propagated by TraceIdMiddleware so every log line in a request shares the same ID.
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


class JsonLogFormatter(logging.Formatter):
    """Emit one JSON object per log line for easy parsing by Loki/ELK later."""

    def __init__(self, service_name: str) -> None:
        super().__init__()
        self._service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "service": self._service_name,
            "level": record.levelname,
            "trace_id": trace_id_var.get(),
            "message": record.getMessage(),
        }
        latency_ms = getattr(record, "latency_ms", None)
        if latency_ms is not None:
            payload["latency_ms"] = latency_ms
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(service_name: str, *, level: int = logging.INFO) -> logging.Logger:
    """Configure root logger once per process; returns a named logger for the service."""
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonLogFormatter(service_name))
        root.addHandler(handler)
        root.setLevel(level)
    return logging.getLogger(service_name)
