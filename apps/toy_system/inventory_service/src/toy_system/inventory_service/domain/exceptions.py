"""Domain exceptions — mapped to HTTP status codes in the API layer."""

from sentinel_core.core.exceptions import SentinelError


class ItemNotFoundError(SentinelError):
    def __init__(self, sku: str) -> None:
        super().__init__(f"SKU not found: {sku}", code="item_not_found")
        self.sku = sku


class InsufficientStockError(SentinelError):
    def __init__(self, sku: str, requested: int, available: int) -> None:
        super().__init__(
            f"Insufficient stock for {sku}: requested {requested}, available {available}",
            code="insufficient_stock",
        )
        self.sku = sku
        self.requested = requested
        self.available = available
