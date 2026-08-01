# AnomalyEvent schema — Detector → Investigator (anomaly_events collection).
# Fields: anomaly_id, service, signal_type (log_pattern | metric_spike),
# confidence, detected_at, raw_evidence_ref.
# This is the first artifact in the pipeline; anomaly_id is the join key everywhere.
