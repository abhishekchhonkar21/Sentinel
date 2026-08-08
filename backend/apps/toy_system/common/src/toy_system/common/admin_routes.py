"""Admin routes for runtime fault injection — included on every toy service."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from toy_system.common.fault_state import FaultState, fault_state_store
from toy_system.common.logging import configure_logging

logger = configure_logging("toy-admin")

FaultStateCallback = Callable[[], Awaitable[None]]
_fault_state_callbacks: list[FaultStateCallback] = []


def register_fault_state_callback(callback: FaultStateCallback) -> None:
    _fault_state_callbacks.append(callback)


async def _notify_fault_state_changed() -> None:
    for callback in _fault_state_callbacks:
        await callback()


class FaultStateResponse(BaseModel):
    state: FaultState


class FaultStatePatch(BaseModel):
    """Partial update — only supplied fields are changed."""

    null_deref: bool | None = None
    latency_delay_ms: int | None = None
    reject_charges: bool | None = None
    rate_limit_enabled: bool | None = None
    rate_limit_max_requests: int | None = None
    rate_limit_window_seconds: float | None = None
    db_latency_delay_ms: int | None = None
    pool_stress_connections: int | None = None
    processing_delay_ms: int | None = None


def build_admin_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

    @router.get("/fault-state", response_model=FaultStateResponse)
    async def get_fault_state() -> FaultStateResponse:
        return FaultStateResponse(state=fault_state_store.get())

    @router.put("/fault-state", response_model=FaultStateResponse)
    async def update_fault_state(patch: FaultStatePatch) -> FaultStateResponse:
        updates: dict[str, Any] = patch.model_dump(exclude_none=True)
        state = fault_state_store.update(updates)
        logger.warning("fault_state_updated fields=%s", list(updates.keys()))
        await _notify_fault_state_changed()
        return FaultStateResponse(state=state)

    @router.post("/fault-state/clear", response_model=FaultStateResponse)
    async def clear_fault_state() -> FaultStateResponse:
        state = fault_state_store.clear()
        logger.info("fault_state_cleared")
        await _notify_fault_state_changed()
        return FaultStateResponse(state=state)

    return router
