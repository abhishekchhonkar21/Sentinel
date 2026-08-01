from critic.api.routes import router
from critic.infrastructure.container import build_app

app = build_app(router)
