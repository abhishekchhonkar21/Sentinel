"""Service bootstrap."""

from toy_system.common.bootstrap import create_toy_service_app
from toy_system.common.http_client import ServiceHttpClient
from toy_system.orders_service.infrastructure.downstream_clients import (
    InventoryClient,
    PaymentsClient,
)
from toy_system.orders_service.infrastructure.settings import get_settings

_http_client: ServiceHttpClient | None = None
_inventory_client: InventoryClient | None = None
_payments_client: PaymentsClient | None = None


def get_clients() -> tuple[InventoryClient, PaymentsClient]:
    if _inventory_client is None or _payments_client is None:
        raise RuntimeError("Downstream clients not initialized")
    return _inventory_client, _payments_client


async def _startup() -> None:
    global _http_client, _inventory_client, _payments_client
    settings = get_settings()
    _http_client = ServiceHttpClient(settings)
    _inventory_client = InventoryClient(http=_http_client, settings=settings)
    _payments_client = PaymentsClient(http=_http_client, settings=settings)


async def _shutdown() -> None:
    global _http_client, _inventory_client, _payments_client
    if _http_client:
        await _http_client.close()
    _http_client = None
    _inventory_client = None
    _payments_client = None


def create_app():
    from toy_system.orders_service.api.routes import router

    return create_toy_service_app(
        title="Orders Service",
        router=router,
        settings=get_settings(),
        on_startup=_startup,
        on_shutdown=_shutdown,
    )
