# api-gateway: single entry point for the toy microservice system.
# Routes incoming HTTP requests to orders-service and downstream dependencies.
# Week 3: emit structured JSON logs (timestamp, service, level, trace_id, message, latency_ms).
# Week 3: expose Prometheus metrics (request count, error rate, latency histograms).
# Fault-injection target: misconfigured rate limits → 429 spikes.
