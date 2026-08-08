from __future__ import annotations

import logging
from datetime import UTC, datetime

from fault_injection.adapters.mongo_fault_catalogue import MongoFaultCatalogueRepository
from fault_injection.adapters.toy_service_client import ToyServiceClient
from fault_injection.domain.injectors.registry import InjectorRegistry
from fault_injection.domain.models import (
    ClearFaultResponse,
    InjectFaultRequest,
    InjectFaultResponse,
    LastFaultAction,
    ServiceFaultStatus,
    SystemStatusResponse,
)
from fault_injection.infrastructure.settings import FaultInjectionSettings
from sentinel_core.core.exceptions import NotFoundError, ValidationError
from sentinel_core.schemas.contracts import FaultCatalogueEntry

logger = logging.getLogger("fault-injection")

_DEFAULT_FAULT_STATE = {
    "null_deref": False,
    "latency_delay_ms": 0,
    "reject_charges": False,
    "rate_limit_enabled": False,
    "rate_limit_max_requests": 2,
    "rate_limit_window_seconds": 1.0,
    "db_latency_delay_ms": 0,
    "pool_stress_connections": 0,
    "processing_delay_ms": 0,
}


def _is_fault_active(state: dict) -> bool:
    for key, default in _DEFAULT_FAULT_STATE.items():
        if state.get(key) != default:
            return True
    return False


class FaultInjectionService:
    def __init__(
        self,
        *,
        registry: InjectorRegistry,
        catalogue: MongoFaultCatalogueRepository,
        toy_client: ToyServiceClient,
        settings: FaultInjectionSettings,
    ) -> None:
        self._registry = registry
        self._catalogue = catalogue
        self._toy_client = toy_client
        self._settings = settings
        self._last_action: LastFaultAction | None = None

    async def list_faults(self) -> list[FaultCatalogueEntry]:
        return await self._catalogue.list_all()

    async def inject(self, request: InjectFaultRequest) -> InjectFaultResponse:
        entry = await self._catalogue.get_by_fault_id(request.fault_id)
        if entry is None:
            raise NotFoundError("fault_catalogue", request.fault_id)

        injector = self._registry.get(request.fault_id)
        injected_at = await injector.inject(request)
        logger.warning(
            "fault_injected fault_id=%s service=%s injected_at=%s",
            request.fault_id,
            entry.injected_service,
            injected_at.isoformat(),
        )

        self._last_action = LastFaultAction(
            action="injected",
            fault_id=request.fault_id,
            service=entry.injected_service,
            at=injected_at,
        )

        return InjectFaultResponse(
            fault_id=request.fault_id,
            injected_at=injected_at,
            status="injected",
            injected_service=entry.injected_service,
            catalogue_entry=entry,
        )

    async def clear_fault(self, service: str) -> ClearFaultResponse:
        try:
            self._settings.service_url(service)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        cleared_at = datetime.now(UTC)
        await self._toy_client.clear_fault_state(service)
        self._last_action = LastFaultAction(
            action="cleared",
            fault_id=None,
            service=service,
            at=cleared_at,
        )
        logger.info("fault_cleared service=%s", service)
        return ClearFaultResponse(
            service=service,
            cleared_at=cleared_at,
            status="cleared",
        )

    async def get_system_status(self) -> SystemStatusResponse:
        faults = await self._catalogue.list_all()
        services: list[ServiceFaultStatus] = []

        for service_name in self._settings.service_names:
            try:
                payload = await self._toy_client.get_fault_state(service_name)
                state = payload.get("state", payload)
            except Exception:
                state = {"error": "unreachable"}
                services.append(
                    ServiceFaultStatus(service=service_name, state=state, active=False)
                )
                continue

            services.append(
                ServiceFaultStatus(
                    service=service_name,
                    state=state,
                    active=_is_fault_active(state),
                )
            )

        return SystemStatusResponse(
            services=services,
            catalogue_count=len(faults),
            last_action=self._last_action,
        )
