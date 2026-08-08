"""Detector service — FastAPI entry point (uvicorn detector.main:app)."""

from detector.api.routes import router
from detector.infrastructure.container import build_app

app = build_app(router)
