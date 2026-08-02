from fastapi import APIRouter
from toy_system.common.bootstrap import create_toy_service_app

router = APIRouter()

def create_app():
    return create_toy_service_app(title="Inventory Service", router=router)
