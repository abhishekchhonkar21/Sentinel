# Service dependency graph: NetworkX in-memory (v1) or Neo4j adapter (optional).
# Encode: api-gateway → orders-service → {payments-service, inventory-service} → external-payment-mock.
# Expose: get_upstream(service), get_downstream(service), get_neighbors(service) for Investigator.
