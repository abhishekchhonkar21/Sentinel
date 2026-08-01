# LangGraph orchestrator FastAPI entry point.
# Expose: POST /investigate-incident (trigger full pipeline), GET /health, GET /incidents/{anomaly_id}.
# Starts the graph on anomaly detection event or manual trigger; returns final IncidentReport.
