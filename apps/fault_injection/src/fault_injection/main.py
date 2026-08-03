"""Fault injection service — POST /inject-fault API + CLI."""

from fault_injection.api.routes import router
from fault_injection.infrastructure.container import build_app

app = build_app(router)
