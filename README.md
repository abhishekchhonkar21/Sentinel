# Sentinel

Autonomous incident-investigation agent — an SRE copilot built on small models, not big reasoning.

## Repository layout

| Path | Purpose |
|------|---------|
| `libs/sentinel_core/` | Shared library: domain models, ports, adapters, `BaseAgent`, app factory |
| `services/` | Deployable agent microservices (detector, investigator, ranker, narrator, critic, orchestrator, api_gateway) |
| `apps/toy_system/` | System under test (4 FastAPI microservices + load generator) |
| `apps/fault_injection/` | Fault injection API + strategy registry |
| `eval/` | Pipeline vs baseline comparison harness |
| `scripts/` | MongoDB seeding, indexes, embeddings |
| `infra/` | Prometheus + Grafana |
| `docs/ARCHITECTURE.md` | Design patterns, layer rules, data flow |

## Architecture principles

- **Hexagonal architecture** — business logic depends on ports (`sentinel_core/ports/`), not MongoDB or Groq directly
- **Layered services** — each microservice has `api/` → `application/` → `domain/` → `infrastructure/`
- **Template Method** — all agents extend `BaseAgent` for tracing, validation, and error handling
- **Strategy + Factory** — swappable detection, scoring, LLM, and graph backends

## Quick start

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e libs/sentinel_core
docker compose up
```

## Run a single service locally

```bash
export PYTHONPATH=libs/sentinel_core/src:services/detector/src
uvicorn detector.main:app --reload --port 8001
```

See `Sentinel_Project_Plan.md` for the 12-week build roadmap and `docs/ARCHITECTURE.md` for design details.
