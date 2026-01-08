"""Models for data quality and validation."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    """Status of data validation."""

    UNVERIFIED = "unverified"
    PENDING_REVIEW = "pending_review"
    PEER_REVIEWED = "peer_reviewed"
    CURATED = "curated"
    REJECTED = "rejected"


class DataQuality(BaseModel):
    """Metadata about the quality and validation status of data."""

    validation_status: ValidationStatus = Field(
        default=ValidationStatus.UNVERIFIED, description="Current validation status"
    )
    requires_review: bool = Field(
        default=False, description="Does this data need manual review?"
    )
    review_notes: Optional[str] = Field(None, description="Notes from reviewers")
    conflicting_sources: List[str] = Field(
        default_factory=list, description="Source IDs that have conflicting data"
    )
    last_validated: Optional[str] = Field(None, description="When was this last validated?")
    validator_id: Optional[str] = Field(None, description="Who validated this data?")
    issues: List[str] = Field(default_factory=list, description="Known issues or caveats")

    class Config:
        json_schema_extra = {
            "example": {
                "validation_status": "peer_reviewed",
                "requires_review": False,
                "conflicting_sources": [],
                "last_validated": "2026-01-08T10:00:00Z",
            }
        }
