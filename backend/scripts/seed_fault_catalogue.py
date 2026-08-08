#!/usr/bin/env python3
"""Seed MongoDB fault_catalogue from backend/apps/fault_injection/catalogue/faults.yaml.

Usage:
    python backend/scripts/seed_fault_catalogue.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import yaml
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "apps" / "fault_injection" / "catalogue" / "faults.yaml"

sys.path.insert(0, str(ROOT / "libs" / "sentinel_core" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "fault_injection" / "src"))

# ruff: noqa: E402
from fault_injection.adapters.mongo_fault_catalogue import MongoFaultCatalogueRepository
from sentinel_core.config.settings import Settings
from sentinel_core.schemas.contracts import FaultCatalogueEntry


def load_catalogue_entries() -> list[FaultCatalogueEntry]:
    with CATALOGUE_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    faults = data.get("faults", [])
    return [FaultCatalogueEntry.model_validate(entry) for entry in faults]


async def seed() -> int:
    settings = Settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client.get_default_database()
    if db is None:
        raise ValueError("MONGODB_URI must include a database name (e.g. .../sentinel)")

    repo = MongoFaultCatalogueRepository(db)
    entries = load_catalogue_entries()
    for entry in entries:
        await repo.upsert(entry)
        print(f"  upserted {entry.fault_id}")

    client.close()
    print(f"Seeded {len(entries)} fault catalogue entries.")
    return len(entries)


def main() -> int:
    try:
        count = asyncio.run(seed())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0 if count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
