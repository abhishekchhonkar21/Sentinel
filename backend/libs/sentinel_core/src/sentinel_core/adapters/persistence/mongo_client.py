"""MongoDB client factory — singleton connection pool shared by all repositories."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from sentinel_core.config.settings import Settings

_client: AsyncIOMotorClient | None = None


def get_mongo_client(settings: Settings | None = None) -> AsyncIOMotorClient:
    """Return a process-wide MongoDB client (lazy init)."""
    global _client
    if _client is None:
        settings = settings or Settings()
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database(settings: Settings | None = None) -> AsyncIOMotorDatabase:
    """Return the default Sentinel database handle."""
    settings = settings or Settings()
    client = get_mongo_client(settings)
    db = client.get_default_database()
    if db is None:
        raise ValueError("MongoDB URI must include a database name")
    return db
