"""Service bootstrap — wires FastAPI app via shared factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from sentinel_core.infrastructure.app_factory import create_service_app


def build_app(router: APIRouter) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        # Startup: warm MongoDB pool, load HF models if needed
        yield
        # Shutdown: close connections

    return create_service_app(
        title="Sentinel Detector",
        version="0.1.0",
        router=router,
        lifespan=lifespan,
    )
