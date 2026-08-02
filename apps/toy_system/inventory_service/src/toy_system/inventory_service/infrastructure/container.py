"""Service bootstrap — connects MongoDB on startup and seeds default catalog."""

from motor.motor_asyncio import AsyncIOMotorClient

from toy_system.common.bootstrap import create_toy_service_app
from toy_system.common.schemas import InventoryItem
from toy_system.inventory_service.adapters.persistence.mongo_inventory_repository import (
    MongoInventoryRepository,
)
from toy_system.inventory_service.api.exception_handlers import register_inventory_exception_handlers
from toy_system.inventory_service.infrastructure.settings import get_settings

DEFAULT_CATALOG = [
    InventoryItem(sku="widget-001", name="Basic Widget", quantity=500, price_cents=1999),
    InventoryItem(sku="widget-pro", name="Pro Widget", quantity=100, price_cents=4999),
    InventoryItem(sku="gadget-100", name="Gadget 100", quantity=250, price_cents=2999),
]

_client: AsyncIOMotorClient | None = None
_repository: MongoInventoryRepository | None = None


def get_repository() -> MongoInventoryRepository:
    if _repository is None:
        raise RuntimeError("Inventory repository not initialized — app lifespan not started")
    return _repository


async def _startup() -> None:
    global _client, _repository
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client.get_default_database()
    if db is None:
        raise ValueError("MONGODB_URI must include a database name (e.g. .../sentinel)")
    _client = client
    _repository = MongoInventoryRepository(db)
    await _repository.seed_if_empty(DEFAULT_CATALOG)


async def _shutdown() -> None:
    global _client
    if _client:
        _client.close()


def create_app():
    from toy_system.inventory_service.api.routes import router

    app = create_toy_service_app(
        title="Inventory Service",
        router=router,
        settings=get_settings(),
        on_startup=_startup,
        on_shutdown=_shutdown,
    )
    register_inventory_exception_handlers(app)
    return app
