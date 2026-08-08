"""Service bootstrap."""

from toy_system.api_gateway.infrastructure.orders_client import OrdersClient
from toy_system.api_gateway.infrastructure.settings import get_settings
from toy_system.common.bootstrap import create_toy_service_app
from toy_system.common.http_client import ServiceHttpClient

_http_client: ServiceHttpClient | None = None
_orders_client: OrdersClient | None = None


def get_orders_client() -> OrdersClient:
    if _orders_client is None:
        raise RuntimeError("Orders client not initialized")
    return _orders_client


async def _startup() -> None:
    global _http_client, _orders_client
    settings = get_settings()
    _http_client = ServiceHttpClient(settings)
    _orders_client = OrdersClient(http=_http_client, settings=settings)


async def _shutdown() -> None:
    global _http_client, _orders_client
    if _orders_client:
        await _orders_client.close()
    _orders_client = None
    _http_client = None


def create_app():
    from toy_system.api_gateway.api.routes import router

    return create_toy_service_app(
        title="API Gateway",
        router=router,
        settings=get_settings(),
        on_startup=_startup,
        on_shutdown=_shutdown,
    )
