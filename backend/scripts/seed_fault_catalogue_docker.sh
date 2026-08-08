#!/usr/bin/env bash
# Seed fault_catalogue via the running fault-injection container (works with Atlas from Docker).
set -euo pipefail
cd "$(dirname "$0")/../../"
docker compose exec fault-injection python -c "
import asyncio, yaml
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from fault_injection.adapters.mongo_fault_catalogue import MongoFaultCatalogueRepository
from fault_injection.infrastructure.settings import get_settings
from sentinel_core.schemas.contracts import FaultCatalogueEntry

async def seed():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client.get_default_database()
    repo = MongoFaultCatalogueRepository(db)
    data = yaml.safe_load(Path('/app/apps/fault_injection/catalogue/faults.yaml').read_text())
    for entry in data['faults']:
        e = FaultCatalogueEntry.model_validate(entry)
        await repo.upsert(e)
        print('  upserted', e.fault_id)
    client.close()
    print(f'Seeded {len(data[\"faults\"])} entries.')

asyncio.run(seed())
"
