"""Domain exceptions for orders-service."""

from sentinel_core.core.exceptions import SentinelError


class InvalidQuantityError(SentinelError):
    def __init__(self, quantity: int) -> None:
        super().__init__(f"Invalid quantity: {quantity}", code="invalid_quantity")
