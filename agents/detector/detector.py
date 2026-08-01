# Core detection logic: statistical + ML anomaly detection on logs and metrics.
# Implement: z-score/EWMA on latency/error-rate, regex log-pattern flags, optional HF log classifier.
# Return AnomalyEvent with confidence score and raw_evidence_ref pointer.
