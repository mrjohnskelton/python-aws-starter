"""Base model class for all entities."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class BaseEntity(BaseModel):
    """Base entity model with common fields for all domain models."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_by: str = Field(..., description="User or system that created this entity")
    last_modified_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    last_modified_by: str = Field(..., description="User or system that last modified this entity")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "entity_001",
                "created_at": "2026-01-08T10:00:00Z",
                "created_by": "system",
                "last_modified_at": "2026-01-08T10:00:00Z",
                "last_modified_by": "system",
            }
        }
    )
