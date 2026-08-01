# orders-service: handles order placement; depends on payments-service and inventory-service.
# Implement realistic failure-prone code paths (not stubs) — null deref after bad deploy, memory leak sim.
# Propagate trace_id in outbound calls for log correlation during incident investigation.
