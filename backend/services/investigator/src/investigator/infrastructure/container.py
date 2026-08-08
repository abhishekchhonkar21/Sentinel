from fastapi import APIRouter, FastAPI

from sentinel_core.infrastructure.app_factory import create_service_app


def build_app(router: APIRouter) -> FastAPI:
    return create_service_app(title="Sentinel Investigator", version="0.1.0", router=router)
