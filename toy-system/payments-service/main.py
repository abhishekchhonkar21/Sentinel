# payments-service: processes payments; depends on external-payment-mock (downstream provider).
# Fault targets: bad deploy null-pointer bug → 500s cascade; external provider timeout simulation.
