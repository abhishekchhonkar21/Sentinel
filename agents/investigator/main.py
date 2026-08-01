# Investigator agent FastAPI app entry point.
# Expose: POST /investigate { anomaly_id } → EvidenceBundle.
# Deterministic retrieval only — no LLM. Query dependency graph, deploys, correlated logs/metrics,
# and past-incident vector similarity (stub empty until Week 9).
