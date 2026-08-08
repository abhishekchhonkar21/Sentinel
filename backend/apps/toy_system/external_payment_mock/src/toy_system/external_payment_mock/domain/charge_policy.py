"""Domain rules for the mock payment provider — no HTTP or config imports."""

from toy_system.common.schemas import ExternalChargeRequest, PaymentStatus


class ChargePolicy:
    """Deterministic charge approval logic.

    Week 1: always approve unless amount is suspiciously high (sanity guard).
    Week 2 fault injection will extend this via settings-driven failure modes.
    """

    MAX_CHARGE_CENTS = 1_000_000  # $10,000 — reject anything above as fraud simulation

    def evaluate(self, request: ExternalChargeRequest) -> PaymentStatus:
        if request.amount_cents > self.MAX_CHARGE_CENTS:
            return PaymentStatus.FAILED
        return PaymentStatus.SUCCEEDED
