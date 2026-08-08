from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from fault_injection.adapters.mongo_fault_catalogue import MongoFaultCatalogueRepository
from fault_injection.adapters.toy_service_client import ToyServiceClient
from fault_injection.application.injection_service import FaultInjectionService
from fault_injection.domain.injectors.registry import InjectorRegistry
from fault_injection.infrastructure.injector_factory import build_injector_registry
from fault_injection.infrastructure.settings import get_settings
from sentinel_core.infrastructure.app_factory import create_service_app

_mongo_client: AsyncIOMotorClient | None = None
_toy_client: ToyServiceClient | None = None
_catalogue: MongoFaultCatalogueRepository | None = None
_registry: InjectorRegistry | None = None
_injection_service: FaultInjectionService | None = None


def get_injection_service() -> FaultInjectionService:
    if _injection_service is None:
        raise RuntimeError("Fault injection service not initialized")
    return _injection_service


async def _startup() -> None:
    global _mongo_client, _toy_client, _catalogue, _registry, _injection_service
    settings = get_settings()
    _mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    db = _mongo_client.get_default_database()
    if db is None:
        raise ValueError("MONGODB_URI must include a database name (e.g. .../sentinel)")
    _toy_client = ToyServiceClient(settings=settings)
    _catalogue = MongoFaultCatalogueRepository(db)
    _registry = build_injector_registry(client=_toy_client)
    _injection_service = FaultInjectionService(
        registry=_registry,
        catalogue=_catalogue,
        toy_client=_toy_client,
        settings=settings,
    )


async def _shutdown() -> None:
    global _mongo_client, _toy_client, _injection_service, _catalogue, _registry
    if _toy_client:
        await _toy_client.close()
    if _mongo_client:
        _mongo_client.close()
    _toy_client = None
    _mongo_client = None
    _catalogue = None
    _registry = None
    _injection_service = None


def build_app(router) -> FastAPI:
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await _startup()
        yield
        await _shutdown()

    app = create_service_app(
        title="Sentinel Fault Injection",
        version="0.1.0",
        router=router,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
