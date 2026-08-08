"""Service-specific settings singleton."""

from functools import lru_cache

from toy_system.common.config import ToyServiceSettings


@lru_cache
def get_settings() -> ToyServiceSettings:
    return ToyServiceSettings(service_name="inventory-service")
