# Toy System — Week 1–2

Four FastAPI microservices + external payment mock, wired for a full order-placement flow.
Week 2 adds a load generator and fault-injection harness.

## Service topology

```
api-gateway (:8080)
    └── orders-service (:8081)
            ├── inventory-service (:8083) → MongoDB
            └── payments-service (:8082)
                    └── external-payment-mock (:8084)
```

## Run locally (no Docker)

### 1. Prerequisites

From the **repo root**:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pip install -e backend/libs/sentinel_core
```

MongoDB must be running locally (inventory-service needs it):

```bash
# macOS (Homebrew)
brew services start mongodb-community

# Or use MongoDB Atlas — set MONGODB_URI in .env
```

### 2. Start all services

```bash
python backend/scripts/run_toy_system.py
```

This starts all five services, waits for health checks, runs a smoke test, and keeps running until Ctrl+C.

### 3. Manual curl (Week 1 exit criterion)

```bash
# Health
curl http://localhost:8080/api/v1/health

# Place an order
curl -X POST http://localhost:8080/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"cust-1","items":[{"sku":"widget-001","quantity":2}]}'
```

Expected response:

```json
{
  "order_id": "ord_...",
  "status": "confirmed",
  "total_cents": 3998,
  "created_at": "..."
}
```

### 4. Run a single service manually

```bash
export PYTHONPATH=\
backend/libs/sentinel_core/src:\
backend/apps/toy_system/common/src:\
backend/apps/toy_system/inventory_service/src

uvicorn toy_system.inventory_service.main:app --reload --port 8083
```

## Internal structure (per service)

```
api/            → HTTP routes (thin controllers)
application/    → use cases / orchestration
domain/         → pure business logic
infrastructure/ → HTTP clients, MongoDB repos, DI container
ports/          → abstract interfaces (inventory-service)
adapters/       → concrete implementations (inventory-service)
```

## Default product catalog

Seeded into MongoDB `inventory_items` on first boot:

| SKU | Name | Stock | Price |
|-----|------|-------|-------|
| widget-001 | Basic Widget | 500 | $19.99 |
| widget-pro | Pro Widget | 100 | $49.99 |
| gadget-100 | Gadget 100 | 250 | $29.99 |

## Docker (optional, when available)

```bash
docker compose up
```

See root `docker-compose.yml` — not required for local development.

## Week 2 — Load generator & fault injection

### Seed fault catalogue

```bash
python backend/scripts/seed_fault_catalogue.py
```

### Start fault injection service

```bash
export PYTHONPATH=backend/libs/sentinel_core/src:backend/apps/fault_injection/src
uvicorn fault_injection.main:app --reload --port 8090
```

### Inject a fault

```bash
python backend/scripts/inject_fault.py --fault-id payments-null-deref
python backend/scripts/inject_fault.py --fault-id payment-provider-timeout
python backend/scripts/inject_fault.py --fault-id api-gateway-rate-limit
python backend/scripts/inject_fault.py --fault-id inventory-db-latency
python backend/scripts/inject_fault.py --fault-id payment-provider-reject
```

### Clear fault state on a service

```bash
curl -X POST http://localhost:8090/api/v1/clear-fault \
  -H "Content-Type: application/json" \
  -d '{"service":"payments-service"}'
```

### Run load generator

```bash
python backend/apps/toy_system/load_generator/generator.py --rps 3
```
