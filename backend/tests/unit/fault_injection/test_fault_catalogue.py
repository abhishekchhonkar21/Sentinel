"""Unit tests for fault catalogue seed data."""

from pathlib import Path

import yaml

from sentinel_core.schemas.contracts import FaultCatalogueEntry

ROOT = Path(__file__).resolve().parents[3]
CATALOGUE_PATH = ROOT / "apps" / "fault_injection" / "catalogue" / "faults.yaml"


def test_fault_catalogue_has_minimum_entries():
    with CATALOGUE_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    faults = data["faults"]
    assert len(faults) >= 15


def test_fault_catalogue_entries_validate():
    with CATALOGUE_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    entries = [FaultCatalogueEntry.model_validate(item) for item in data["faults"]]
    fault_ids = {entry.fault_id for entry in entries}
    assert len(fault_ids) == len(entries)

    required_first_five = {
        "payments-null-deref",
        "payment-provider-timeout",
        "api-gateway-rate-limit",
        "inventory-db-latency",
        "payment-provider-reject",
    }
    assert required_first_five.issubset(fault_ids)
