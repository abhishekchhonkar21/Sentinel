"""Shared observability for toy-system services — JSON logs + Prometheus."""

from sentinel_core.infrastructure.app_factory import create_service_app
from fastapi import APIRouter


def create_toy_service_app(*, title: str, router: APIRouter):
    """Thin wrapper around sentinel_core app factory for toy microservices."""
    return create_service_app(title=title, version="0.1.0", router=router)
