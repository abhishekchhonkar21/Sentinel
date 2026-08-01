# Evidence assembly logic: given anomaly_id, build EvidenceBundle (Section 6.2).
# Query: graph.get_neighbors(), MongoDB deploys, raw_logs/metrics time window around detected_at,
# Atlas Vector Search on incident_reports for related_past_incidents.
