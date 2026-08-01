# Sentinel

Autonomous incident-investigation agent — an SRE copilot built on small models, not big reasoning.

## What this repo contains

- **toy-system/** — 4 FastAPI microservices + load generator (the system under test)
- **agents/** — Detector, Investigator, Hypothesis-Ranker, Narrator, Critic (one FastAPI service each)
- **orchestrator/** — LangGraph pipeline wiring agent services end-to-end
- **shared/** — Pydantic schemas and MongoDB helpers (agent communication contracts)
- **fault-injection/** — CLI/API to inject cataloged faults for eval ground truth
- **eval/** — Baseline comparison and full fault-catalogue eval harness (resume numbers live here)
- **scripts/** — One-off utilities (seed fault catalogue, simulate deploys)
- **infra/** — Prometheus and Grafana config for toy system + agent observability

## Quick start (once implemented)

```bash
cp .env.example .env
docker compose up
```

See `Sentinel_Project_Plan.md` (or `PLAN.md`) for the full build roadmap.
