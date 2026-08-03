from orchestrator.api.routes import router
from orchestrator.infrastructure.container import build_app

app = build_app(router)
