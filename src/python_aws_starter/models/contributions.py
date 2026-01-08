"""Models for user contributions and edits."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ContributionType(str, Enum):
    """Type of user contribution."""

    NEW_ENTRY = "new_entry"
    EDIT = "edit"
    CONFLICT_RESOLUTION = "conflict_resolution"
    SOURCE_ADDITION = "source_addition"
    CORRECTION = "correction"


class ContributionStatus(str, Enum):
    """Status of a user contribution."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"


class UserContribution(BaseModel):
    """Tracks a user's contribution to the timeline data."""

    id: str = Field(..., description="Unique identifier for this contribution")
    user_id: str = Field(..., description="ID of the user making the contribution")
    entity_type: str = Field(
        ...,
        description="Type of entity being contributed (event, person, geography)",
    )
    entity_id: str = Field(..., description="ID of the entity being modified or created")
    
    contribution_type: ContributionType = Field(
        ..., description="Type of contribution"
    )
    status: ContributionStatus = Field(
        default=ContributionStatus.PENDING, description="Current status of contribution"
    )
    
    # Original and modified data
    original_data: Optional[Dict[str, Any]] = Field(
        None, description="Data before modification (null for new entries)"
    )
    modified_data: Dict[str, Any] = Field(
        ..., description="Data after modification or new data"
    )
    
    # Justification
    justification: str = Field(
        ..., description="Why this change was made"
    )
    change_summary: Optional[str] = Field(
        None, description="Brief summary of changes"
    )
    
    # Moderation
    moderator_id: Optional[str] = Field(
        None, description="User who approved/rejected this"
    )
    moderation_notes: Optional[str] = Field(
        None, description="Notes from the moderator"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    reviewed_at: Optional[datetime] = Field(None, description="When was this reviewed?")
    merged_at: Optional[datetime] = Field(None, description="When was this merged?")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "contrib_001",
                "user_id": "user_123",
                "entity_type": "event",
                "entity_id": "event_wwii_001",
                "contribution_type": "edit",
                "status": "pending",
                "original_data": {"title": "WW2"},
                "modified_data": {"title": "World War II", "description": "Updated description"},
                "justification": "Fixed spelling and added more details",
                "created_at": "2026-01-08T10:00:00Z",
            }
        }
    )
