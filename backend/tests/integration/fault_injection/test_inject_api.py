"""Integration tests for fault injection API (in-process, mocked dependencies)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from fault_injection.application.injection_service import FaultInjectionService
from fault_injection.infrastructure.settings import FaultInjectionSettings
from sentinel_core.domain.enums import SignalType
from sentinel_core.schemas.contracts import FaultCatalogueEntry


@pytest.fixture
def fault_injection_client():
    import fault_injection.infrastructure.container as container

    mock_catalogue = AsyncMock()
    mock_catalogue.get_by_fault_id.return_value = FaultCatalogueEntry(
        fault_id="payments-null-deref",
        description="test",
        injected_service="payments-service",
        true_root_cause="bad deploy",
        expected_signal_type=SignalType.LOG_PATTERN,
    )
    mock_catalogue.list_all.return_value = []

    mock_injector = AsyncMock()
    mock_injector.inject.return_value = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_injector

    container._injection_service = FaultInjectionService(
        registry=mock_registry,
        catalogue=mock_catalogue,
        toy_client=AsyncMock(),
        settings=FaultInjectionSettings(),
    )

    from fault_injection.main import app

    yield TestClient(app)
    container._injection_service = None


def test_inject_fault_returns_timestamp(fault_injection_client):
    response = fault_injection_client.post(
        "/api/v1/inject-fault",
        json={"fault_id": "payments-null-deref"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["fault_id"] == "payments-null-deref"
    assert body["injected_service"] == "payments-service"
    assert body["injected_at"].startswith("2026-08-08T12:00:00")
