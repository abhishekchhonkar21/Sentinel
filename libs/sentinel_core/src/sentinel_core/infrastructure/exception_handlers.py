"""Map domain exceptions to HTTP responses at the API boundary."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from sentinel_core.core.exceptions import NotFoundError, SentinelError, ValidationError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"code": exc.code, "message": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"code": exc.code, "message": exc.message})

    @app.exception_handler(SentinelError)
    async def sentinel_handler(_request: Request, exc: SentinelError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"code": exc.code, "message": exc.message})
