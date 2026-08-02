# TODO: FastAPI routes for order placement flow through api-gateway
# Use toy_system.common.bootstrap.create_toy_service_app for consistent setup

from fastapi import APIRouter

from toy_system.common.bootstrap import create_toy_service_app

router = APIRouter()


def create_app():
    return create_toy_service_app(title="API Gateway", router=router)
