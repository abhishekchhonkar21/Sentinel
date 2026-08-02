"""Service bootstrap."""

from toy_system.common.bootstrap import create_toy_service_app
from toy_system.common.http_client import ServiceHttpClient
from toy_system.payments_service.infrastructure.external_payment_client import ExternalPaymentClient
from toy_system.payments_service.infrastructure.settings import get_settings

_http_client: ServiceHttpClient | None = None
_external_client: ExternalPaymentClient | None = None


def get_external_client() -> ExternalPaymentClient:
    if _external_client is None:
        raise RuntimeError("External payment client not initialized")
    return _external_client


async def _startup() -> None:
    global _http_client, _external_client
    settings = get_settings()
    _http_client = ServiceHttpClient(settings)
    _external_client = ExternalPaymentClient(http=_http_client, settings=settings)


async def _shutdown() -> None:
    global _http_client, _external_client
    if _external_client:
        await _external_client.close()
    _external_client = None
    _http_client = None


def create_app():
    from toy_system.payments_service.api.routes import router

    return create_toy_service_app(
        title="Payments Service",
        router=router,
        settings=get_settings(),
        on_startup=_startup,
        on_shutdown=_shutdown,
    )
