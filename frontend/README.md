# Sentinel Frontend

Simple dashboard for controlling the toy system fault injection harness.

## Prerequisites

- Fault injection API running on port **8090** (`docker compose up` or local uvicorn)
- MongoDB seeded with the fault catalogue (`python backend/scripts/seed_fault_catalogue.py`)

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

The Vite dev server proxies `/api` to `http://localhost:8090`.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `""` (use proxy) | Base URL for fault-injection API |

## Features

- Browse the full fault catalogue from MongoDB
- **Inject fault** — triggers `POST /api/v1/inject-fault`
- **Clear service** — resets runtime fault state via `POST /api/v1/clear-fault`
- Live summary: active fault count, last action, per-service fault state (auto-refresh every 5s)
