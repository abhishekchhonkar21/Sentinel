# Detector agent FastAPI app entry point.
# Expose: GET /health, POST /detect (or background polling worker started on startup).
# Consumes recent logs/metrics windows from MongoDB raw_logs; writes AnomalyEvent to anomaly_events.
# No LLM — classical ML / small HF model only (Week 4 v1: z-score/EWMA; Week 5 v2: fine-tuned classifier).
