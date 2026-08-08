"""Service discovery URLs for the toy microservice mesh.

Each service reads only the URLs it needs. Defaults match docker-compose service names.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ToyServiceSettings(BaseSettings):
    """Environment-driven configuration shared across toy-system services."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Identity — set per container so logs/metrics are attributed correctly.
    service_name: str = "toy-service"

    # Downstream service URLs — localhost defaults for local dev (no Docker).
    # Override in .env or docker-compose when running in containers.
    orders_service_url: str = "http://localhost:8081"
    payments_service_url: str = "http://localhost:8082"
    inventory_service_url: str = "http://localhost:8083"
    external_payment_url: str = "http://localhost:8084"

    # MongoDB — inventory-service is the only toy service that talks to the DB directly.
    mongodb_uri: str = "mongodb://localhost:27017/sentinel"

    # Fault-injection toggles (Week 2 harness will flip these programmatically).
    fault_null_deref: bool = False
    fault_payment_timeout_ms: int = 0

    # HTTP client tuning.
    http_timeout_seconds: float = 10.0
