# Fault-injection FastAPI service entry point.
# Expose: POST /inject-fault { fault_id | type, service, params } — triggers cataloged failure modes.
# Log exact injection timestamp to MongoDB for eval harness alignment with anomaly detection timing.
