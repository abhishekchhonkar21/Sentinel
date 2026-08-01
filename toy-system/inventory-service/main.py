# inventory-service: manages stock; reads/writes MongoDB (real DB dependency for pool exhaustion faults).
# Week 1: wire to MongoDB collection acting as inventory data store.
# Fault targets: connection pool exhaustion → latency spike without hard errors.
