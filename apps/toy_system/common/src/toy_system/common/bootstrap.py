"""FastAPI bootstrap for toy-system microservices."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from sentinel_core.infrastructure.app_factory import create_service_app
from toy_system.common.config import ToyServiceSettings
from toy_system.common.logging import configure_logging
from toy_system.common.middleware import TraceIdMiddleware

StartupFn = Callable[[], Awaitable[None]]
ShutdownFn = Callable[[], Awaitable[None]]


def create_toy_service_app(
    *,
    title: str,
    router: APIRouter,
    settings: ToyServiceSettings,
    on_startup: StartupFn | None = None,
    on_shutdown: ShutdownFn | None = None,
) -> FastAPI:
    """Factory — wires logging, trace middleware, metrics, and optional lifespan hooks."""

    configure_logging(settings.service_name)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if on_startup:
            await on_startup()
        yield
        if on_shutdown:
            await on_shutdown()

    app = create_service_app(title=title, version="0.1.0", router=router, lifespan=lifespan)
    app.add_middleware(TraceIdMiddleware, service_name=settings.service_name)
    app.state.settings = settings
    return app
