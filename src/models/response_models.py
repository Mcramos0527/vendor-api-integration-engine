"""
Pydantic response models for the Vendor API Integration Engine.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SpecialBidResponse(BaseModel):
    """Successful IDoc creation response."""

    status: str = Field(default="success")
    idoc_id: str = Field(description="Generated IDoc document identifier")
    opgan: str = Field(description="OPGAN reference (MCN_TransactionNumber)")
    product_category: str = Field(description="Classified product category")
    processing_mode: str = Field(description="INITIAL or UPDATE")
    timestamp: datetime = Field(description="Processing timestamp (UTC)")
    request_id: str = Field(description="Unique request tracking identifier")


class ErrorResponse(BaseModel):
    """Validation error response."""

    status: str = Field(default="validation_error")
    errors: List[str] = Field(description="List of validation error messages")
    request_id: str = Field(description="Unique request tracking identifier")


class DuplicateResponse(BaseModel):
    """Duplicate record response."""

    status: str = Field(default="duplicate")
    message: str = Field(description="Duplicate detection message")
    existing_idoc_id: str = Field(description="ID of the existing IDoc")
    composite_key: str = Field(description="The composite key that was matched")
    request_id: str = Field(description="Unique request tracking identifier")


class IDocStatusResponse(BaseModel):
    """IDoc processing status response."""

    idoc_id: str
    opgan: str
    status: str = Field(description="Current processing status")
    product_category: str
    processing_mode: str
    created_at: datetime
    updated_at: Optional[datetime] = None
