# Sentinel

Autonomous incident-investigation agent — an SRE copilot built on small models, not big reasoning.

## Repository layout

| Path | Purpose |
|------|---------|
| `backend/libs/sentinel_core/` | Shared library: domain models, ports, adapters, `BaseAgent`, app factory |
| `backend/services/` | Deployable agent microservices (detector, investigator, ranker, narrator, critic, orchestrator, api_gateway) |
| `backend/apps/toy_system/` | System under test (4 FastAPI microservices + load generator) |
| `backend/apps/fault_injection/` | Fault injection API + strategy registry |
| `backend/eval/` | Pipeline vs baseline comparison harness |
| `backend/scripts/` | MongoDB seeding, indexes, embeddings |
| `frontend/` | React dashboard for fault injection (Week 2) |
| `infra/` | Prometheus + Grafana |
| `docs/ARCHITECTURE.md` | Design patterns, layer rules, data flow |

## Architecture principles

- **Hexagonal architecture** — business logic depends on ports (`sentinel_core/ports/`), not MongoDB or Groq directly
- **Layered services** — each microservice has `api/` → `application/` → `domain/` → `infrastructure/`
- **Template Method** — all agents extend `BaseAgent` for tracing, validation, and error handling
- **Strategy + Factory** — swappable detection, scoring, LLM, and graph backends

## Quick start (local — no Docker)

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements-dev.txt
pip install -e backend/libs/sentinel_core

# Requires MongoDB on localhost:27017 (or set MONGODB_URI in .env)
python backend/scripts/run_toy_system.py
```

See `backend/apps/toy_system/README.md` for the full order-flow curl example.

## Quick start (Docker — optional)

```bash
docker compose up
```

## Frontend (fault injection dashboard)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) (proxies `/api` to fault-injection on `:8090`).

See `frontend/README.md` for prerequisites.

## Run a single agent service locally

```bash
export PYTHONPATH=backend/libs/sentinel_core/src:backend/services/detector/src
uvicorn detector.main:app --reload --port 8001
```

See `Sentinel_Project_Plan.md` for the 12-week build roadmap and `docs/ARCHITECTURE.md` for design details.
