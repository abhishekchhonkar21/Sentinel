"""Public incident report API — read-only facade over MongoDB."""

from api_gateway.api.routes import router
from api_gateway.infrastructure.container import build_app

app = build_app(router)
