from hypothesis_ranker.api.routes import router
from hypothesis_ranker.infrastructure.container import build_app

app = build_app(router)
