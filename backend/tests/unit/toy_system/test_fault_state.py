"""Unit tests for runtime fault state."""

from toy_system.common.fault_state import FaultState, FaultStateStore


def test_fault_state_clear_resets_all_fields():
    store = FaultStateStore()
    store.update({"null_deref": True, "latency_delay_ms": 500})
    cleared = store.clear()
    assert cleared.null_deref is False
    assert cleared.latency_delay_ms == 0


def test_fault_state_apply_patch_ignores_unknown_fields():
    state = FaultState()
    updated = state.apply_patch({"null_deref": True, "unknown_field": 99})
    assert updated.null_deref is True
    assert not hasattr(updated, "unknown_field")
