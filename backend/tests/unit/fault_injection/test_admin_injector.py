"""Unit tests for fault injection injectors."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from fault_injection.domain.injectors.admin_injector import AdminFaultInjector
from fault_injection.domain.models import InjectFaultRequest


@pytest.mark.asyncio
async def test_admin_fault_injector_merges_params():
    client = AsyncMock()
    client.update_fault_state.return_value = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)

    injector = AdminFaultInjector(
        fault_id="payment-provider-timeout",
        service_name="external-payment-mock",
        default_state={"latency_delay_ms": 8000},
        client=client,
    )

    request = InjectFaultRequest(
        fault_id="payment-provider-timeout",
        params={"latency_delay_ms": 3000},
    )
    injected_at = await injector.inject(request)

    client.update_fault_state.assert_awaited_once_with(
        "external-payment-mock",
        {"latency_delay_ms": 3000},
    )
    assert injected_at.year == 2026
