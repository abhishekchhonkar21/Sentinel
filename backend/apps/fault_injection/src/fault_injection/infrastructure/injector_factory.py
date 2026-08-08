"""Build and wire the injector registry with all catalogue-backed strategies."""

from fault_injection.adapters.toy_service_client import ToyServiceClient
from fault_injection.domain.injectors.admin_injector import AdminFaultInjector
from fault_injection.domain.injectors.registry import InjectorRegistry

# fault_id -> (target service, default admin fault-state patch)
INJECTOR_DEFINITIONS: list[tuple[str, str, dict]] = [
    ("payments-null-deref", "payments-service", {"null_deref": True}),
    ("payment-null-deref-eval", "payments-service", {"null_deref": True}),
    ("payments-null-deref-cascade", "payments-service", {"null_deref": True}),
    ("payment-provider-timeout", "external-payment-mock", {"latency_delay_ms": 8000}),
    ("provider-timeout-eval", "external-payment-mock", {"latency_delay_ms": 8000}),
    ("payments-timeout-cascade", "external-payment-mock", {"latency_delay_ms": 12000}),
    ("payment-provider-slow", "external-payment-mock", {"latency_delay_ms": 2000}),
    ("payment-provider-reject", "external-payment-mock", {"reject_charges": True}),
    (
        "external-payment-intermittent-reject",
        "external-payment-mock",
        {"reject_charges": True},
    ),
    (
        "api-gateway-rate-limit",
        "api-gateway",
        {
            "rate_limit_enabled": True,
            "rate_limit_max_requests": 2,
            "rate_limit_window_seconds": 1.0,
        },
    ),
    (
        "api-gateway-strict-rate-limit",
        "api-gateway",
        {
            "rate_limit_enabled": True,
            "rate_limit_max_requests": 1,
            "rate_limit_window_seconds": 1.0,
        },
    ),
    (
        "gateway-rate-limit-moderate",
        "api-gateway",
        {
            "rate_limit_enabled": True,
            "rate_limit_max_requests": 5,
            "rate_limit_window_seconds": 1.0,
        },
    ),
    ("inventory-db-latency", "inventory-service", {"db_latency_delay_ms": 1500}),
    ("inventory-db-latency-mild", "inventory-service", {"db_latency_delay_ms": 500}),
    ("inventory-high-db-latency", "inventory-service", {"db_latency_delay_ms": 3000}),
    ("inventory-pool-stress", "inventory-service", {"pool_stress_connections": 10}),
    ("inventory-pool-stress-heavy", "inventory-service", {"pool_stress_connections": 25}),
    ("orders-processing-delay", "orders-service", {"processing_delay_ms": 2000}),
    ("orders-slow-processing", "orders-service", {"processing_delay_ms": 1000}),
    ("orders-delay-heavy", "orders-service", {"processing_delay_ms": 4000}),
]


def build_injector_registry(
    *,
    client: ToyServiceClient,
) -> InjectorRegistry:
    registry = InjectorRegistry()
    for fault_id, service_name, default_state in INJECTOR_DEFINITIONS:
        registry.register(
            AdminFaultInjector(
                fault_id=fault_id,
                service_name=service_name,
                default_state=default_state,
                client=client,
            )
        )
    return registry
