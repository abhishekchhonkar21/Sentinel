"""Runtime fault toggles — mutated by the Week 2 fault-injection harness.

Each toy-service process holds its own in-memory state. Injectors flip these via
the admin API without restarting containers or editing environment variables.
"""

from __future__ import annotations

import threading
from typing import Any

from pydantic import BaseModel, Field


class FaultState(BaseModel):
    """All supported fault knobs — services read only the fields they care about."""

    null_deref: bool = False
    latency_delay_ms: int = Field(default=0, ge=0)
    reject_charges: bool = False
    rate_limit_enabled: bool = False
    rate_limit_max_requests: int = Field(default=2, ge=1)
    rate_limit_window_seconds: float = Field(default=1.0, gt=0)
    db_latency_delay_ms: int = Field(default=0, ge=0)
    pool_stress_connections: int = Field(default=0, ge=0)
    processing_delay_ms: int = Field(default=0, ge=0)

    def apply_patch(self, patch: dict[str, Any]) -> FaultState:
        """Return a new state with only known fields updated."""
        allowed = set(FaultState.model_fields)
        updates = {k: v for k, v in patch.items() if k in allowed}
        return self.model_copy(update=updates)

    def clear(self) -> FaultState:
        return FaultState()


class FaultStateStore:
    """Thread-safe holder for the process-wide fault state."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state = FaultState()

    def get(self) -> FaultState:
        with self._lock:
            return self._state.model_copy()

    def update(self, patch: dict[str, Any]) -> FaultState:
        with self._lock:
            self._state = self._state.apply_patch(patch)
            return self._state.model_copy()

    def clear(self) -> FaultState:
        with self._lock:
            self._state = FaultState()
            return self._state.model_copy()


# One store per process — admin routes and business logic share this instance.
fault_state_store = FaultStateStore()
