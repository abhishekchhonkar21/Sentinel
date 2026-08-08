"""Investigator agent — subclasses BaseAgent; deterministic evidence assembly."""

from investigator.api.routes import router
from investigator.infrastructure.container import build_app

app = build_app(router)
