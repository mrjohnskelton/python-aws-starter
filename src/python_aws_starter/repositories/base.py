"""Base repository class for all data access patterns."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository for data access."""

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get a single entity by ID."""
        pass

    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """List entities with optional filtering and pagination."""
        pass

    @abstractmethod
    async def create(self, data: T) -> T:
        """Create a new entity."""
        pass

    @abstractmethod
    async def update(self, entity_id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update an existing entity."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity."""
        pass

    @abstractmethod
    async def search(self, query: str) -> List[T]:
        """Search entities by full-text search."""
        pass
