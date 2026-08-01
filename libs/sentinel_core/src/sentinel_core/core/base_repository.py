"""Generic repository base — implement concrete MongoDB repos in adapters/persistence/."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

TEntity = TypeVar("TEntity", bound=BaseModel)


class BaseRepository(ABC, Generic[TEntity]):
    """Abstract repository defining standard persistence operations.

    Concrete subclasses (e.g. MongoAnomalyEventRepository) live in
    sentinel_core.adapters.persistence and are injected via FastAPI Depends.
    """

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> TEntity | None:
        """Fetch a single document by its business key (e.g. anomaly_id)."""

    @abstractmethod
    async def save(self, entity: TEntity) -> TEntity:
        """Insert or upsert a document."""

    @abstractmethod
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[TEntity]:
        """Paginated listing for admin/debug endpoints."""
