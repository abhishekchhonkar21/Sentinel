"""API gateway — single entry point for the toy microservice mesh."""

from toy_system.api_gateway.infrastructure.container import create_app

app = create_app()
