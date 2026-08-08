"""Service bootstrap."""

from toy_system.common.bootstrap import create_toy_service_app
from toy_system.external_payment_mock.infrastructure.settings import get_settings


def create_app():
    # Lazy import avoids circular dependency: routes → dependencies → settings
    from toy_system.external_payment_mock.api.routes import router

    return create_toy_service_app(
        title="External Payment Mock",
        router=router,
        settings=get_settings(),
    )
