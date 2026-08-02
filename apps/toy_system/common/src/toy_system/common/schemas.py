"""Cross-service DTOs for the order-placement flow.

These models are the public contract between toy microservices. Keeping them in the
shared library avoids duplication and ensures api-gateway ↔ orders ↔ payments ↔
inventory all speak the same language.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class OrderStatus(StrEnum):
    CONFIRMED = "confirmed"
    FAILED = "failed"


class PaymentStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Order flow (api-gateway → orders-service)
# ---------------------------------------------------------------------------


class OrderItem(BaseModel):
    sku: str = Field(min_length=1, description="Stock-keeping unit identifier")
    quantity: int = Field(gt=0, description="Units to purchase")


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    items: list[OrderItem] = Field(min_length=1)


class CreateOrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    total_cents: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Inventory (orders-service → inventory-service)
# ---------------------------------------------------------------------------


class InventoryItem(BaseModel):
    sku: str
    name: str
    quantity: int = Field(ge=0)
    price_cents: int = Field(ge=0)


class ReserveStockRequest(BaseModel):
    order_id: str
    sku: str
    quantity: int = Field(gt=0)


class ReserveStockResponse(BaseModel):
    order_id: str
    sku: str
    reserved: int
    remaining: int


# ---------------------------------------------------------------------------
# Payments (orders-service → payments-service → external-payment-mock)
# ---------------------------------------------------------------------------


class ChargePaymentRequest(BaseModel):
    order_id: str
    amount_cents: int = Field(gt=0)
    currency: str = "USD"


class ChargePaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    status: PaymentStatus
    amount_cents: int


class ExternalChargeRequest(BaseModel):
    """Payload sent from payments-service to the external provider mock."""

    order_id: str
    amount_cents: int = Field(gt=0)
    currency: str = "USD"


class ExternalChargeResponse(BaseModel):
    transaction_id: str
    status: PaymentStatus
