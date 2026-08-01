"""FastAPI application factory — consistent service bootstrap across all agents."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from sentinel_core.infrastructure.exception_handlers import register_exception_handlers
from sentinel_core.infrastructure.observability import setup_metrics_route


def create_service_app(
    *,
    title: str,
    version: str,
    router: APIRouter,
    lifespan: Callable[[FastAPI], AsyncIterator[None]] | None = None,
) -> FastAPI:
    """Factory Method — every microservice calls this instead of raw FastAPI()."""
    app = FastAPI(title=title, version=version, lifespan=lifespan)
    app.include_router(router)
    register_exception_handlers(app)
    setup_metrics_route(app)
    return app
