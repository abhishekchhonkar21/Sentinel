"""Map inventory domain exceptions to HTTP status codes."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from toy_system.inventory_service.domain.exceptions import InsufficientStockError, ItemNotFoundError


def register_inventory_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ItemNotFoundError)
    async def item_not_found(_request: Request, exc: ItemNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"code": exc.code, "message": exc.message})

    @app.exception_handler(InsufficientStockError)
    async def insufficient_stock(_request: Request, exc: InsufficientStockError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"code": exc.code, "message": exc.message})
