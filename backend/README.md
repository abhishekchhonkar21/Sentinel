# Backend

Python services, shared libraries, eval harness, and operational scripts for Sentinel.

## Layout

| Path | Purpose |
|------|---------|
| `libs/sentinel_core/` | Shared domain models, ports, adapters, `BaseAgent` |
| `services/` | Agent microservices (detector, investigator, ranker, narrator, critic, orchestrator) |
| `apps/toy_system/` | System under test — 4 microservices + load generator |
| `apps/fault_injection/` | Fault injection API + catalogue |
| `eval/` | Pipeline vs baseline comparison harness |
| `scripts/` | DB seeding, local dev runners |
| `tests/` | Unit and integration tests |

Install dependencies from the **repo root**:

```bash
pip install -r backend/requirements-dev.txt
pip install -e backend/libs/sentinel_core
```

Run tests from the **repo root** (`pytest` reads `pyproject.toml` at root):

```bash
pytest
```

Toy system and fault injection details: `apps/toy_system/README.md`.
