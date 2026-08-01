# MongoDB client singleton / connection pool.
# Expose get_database() and handle Atlas vs local mongod URI from shared.config.
# Add retry logic for transient connection failures during docker compose startup.
