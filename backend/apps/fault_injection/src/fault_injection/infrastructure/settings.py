"""Fault injection service settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class FaultInjectionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017/sentinel"
    http_timeout_seconds: float = 15.0

    api_gateway_url: str = "http://localhost:8080"
    orders_service_url: str = "http://localhost:8081"
    payments_service_url: str = "http://localhost:8082"
    inventory_service_url: str = "http://localhost:8083"
    external_payment_url: str = "http://localhost:8084"

    @property
    def service_names(self) -> list[str]:
        return [
            "api-gateway",
            "orders-service",
            "payments-service",
            "inventory-service",
            "external-payment-mock",
        ]

    def service_url(self, service_name: str) -> str:
        mapping = {
            "api-gateway": self.api_gateway_url,
            "orders-service": self.orders_service_url,
            "payments-service": self.payments_service_url,
            "inventory-service": self.inventory_service_url,
            "external-payment-mock": self.external_payment_url,
        }
        if service_name not in mapping:
            raise ValueError(f"Unknown service: {service_name}")
        return mapping[service_name].rstrip("/")


@lru_cache
def get_settings() -> FaultInjectionSettings:
    return FaultInjectionSettings()
