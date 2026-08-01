# Critic/verifier agent FastAPI app entry point (Week 10, v1.5).
# Expose: POST /verify { incident_report, evidence_bundle } → { grounded: bool, flagged_claims[] }.
# Constrained LLM or string/entity matching: every narrator claim must trace to evidence bundle.
