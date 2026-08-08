"""Pure pricing logic — no I/O."""

from toy_system.orders_service.domain.exceptions import InvalidQuantityError


class OrderPricing:
    """Domain service for computing line totals."""

    def line_total(self, price_cents: int, quantity: int) -> int:
        if quantity <= 0:
            raise InvalidQuantityError(quantity)
        return price_cents * quantity
