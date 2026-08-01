from narrator.api.routes import router
from narrator.infrastructure.container import build_app

app = build_app(router)
