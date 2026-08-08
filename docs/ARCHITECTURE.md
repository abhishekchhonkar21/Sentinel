# Sentinel Architecture

## Layout (monorepo)

```
backend/
├── libs/sentinel_core/     # Shared library — domain, ports, adapters, infrastructure
├── services/               # Deployable agent microservices (hexagonal / clean architecture)
├── apps/                   # Toy system under test + fault injection
├── eval/                   # Benchmark harness
├── scripts/                # DB seeding and maintenance
└── tests/                  # unit/ and integration/
frontend/                   # React dashboard (fault injection UI)
infra/                      # Prometheus, Grafana
```

## Design patterns

| Pattern | Where | Purpose |
|---------|-------|---------|
| **Hexagonal (Ports & Adapters)** | `sentinel_core/ports/` + `adapters/` | Swap MongoDB, Neo4j, Groq/Gemini without touching business logic |
| **Template Method** | `BaseAgent.run()` | Shared validate → execute → trace lifecycle for all agents |
| **Strategy** | `AnomalyDetectionStrategy`, `HypothesisScorer`, `LLMProvider` | Pluggable detection, scoring, and LLM backends |
| **Composite** | `CompositeDetectionStrategy` | Chain multiple detectors |
| **Factory** | `build_graph_store()`, `build_llm_provider()`, `create_service_app()` | Consistent object construction |
| **Repository** | `ports/repositories.py` + `adapters/persistence/` | Persistence abstraction over MongoDB |
| **Registry** | `InjectorRegistry`, `CompositeDetectionStrategy.register()` | Map IDs to implementations |
| **Dependency Injection** | FastAPI `Depends()` + `infrastructure/dependencies.py` | Wire ports to adapters at runtime |

## Service internal layers

Every service under `backend/services/` follows the same structure:

```
service/
├── src/service_name/
│   ├── main.py              # Uvicorn entry point
│   ├── api/                 # HTTP controllers (thin — no business logic)
│   │   ├── routes.py
│   │   └── dependencies.py  # Service-local DI
│   ├── application/         # Use cases / agents (orchestration)
│   ├── domain/              # Pure business logic (no FastAPI, no MongoDB)
│   └── infrastructure/      # Service bootstrap, external clients
└── Dockerfile
```

**Dependency rule:** `api` → `application` → `domain` ← `infrastructure` implements ports from `backend/libs/sentinel_core`.

## Data flow

```
AnomalyEvent → InvestigatorAgent → EvidenceBundle → HypothesisRankerAgent
    → RankedHypotheses → NarratorAgent → IncidentReport → CriticAgent → CriticVerdict
```

Orchestrator (`backend/services/orchestrator/`) drives this via LangGraph, calling each agent over HTTP.
