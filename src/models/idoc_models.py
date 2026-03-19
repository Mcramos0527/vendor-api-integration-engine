"""
IDoc (Intermediate Document) models for ERP integration.

IDocs are the standard format for exchanging data with ERP systems.
This module defines the structure of generated IDoc documents.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class IDocHeader(BaseModel):
    """IDoc control record — identifies the document type and routing."""

    idoc_id: str = Field(description="Unique IDoc document identifier")
    doc_type: str = Field(
        default="ZSDA",
        description="IDoc document type for sales agreement creation",
    )
    opgan: str = Field(description="OPGAN business reference")
    processing_mode: str = Field(description="INITIAL or UPDATE")
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    source_system: str = Field(default="VENDOR_API")
    target_system: str = Field(default="ERP")


class IDocSegment(BaseModel):
    """IDoc data segment — contains the transformed business data."""

    customer_name: str
    customer_id: str
    reseller_partner: str
    orderable_part_number: str
    remaining_quantity: int
    entitled_price: float
    currency: str
    region: str
    fulfilment_type: str
    product_category: str
    product_brand: str


class IDocDocument(BaseModel):
    """Complete IDoc document ready for ERP ingestion."""

    header: IDocHeader
    segment: IDocSegment
    audit: Dict[str, Any] = Field(
        default_factory=dict,
        description="Audit metadata for traceability",
    )

    @property
    def idoc_id(self) -> str:
        return self.header.idoc_id

    @property
    def opgan(self) -> str:
        return self.header.opgan
