"""
Pydantic request models for the Vendor API Integration Engine.

These models define the expected JSON schema for incoming vendor payloads
and enforce validation at the API boundary.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SpecialBidRequest(BaseModel):
    """
    Schema for a special bid / pricing record submitted by a vendor system.

    This model validates the incoming JSON payload before it enters
    the processing pipeline. Fields map to vendor API dictionary fields.
    """

    mcn: str = Field(
        ...,
        description="Master Contract Number — unique identifier for the vendor agreement",
        examples=["MCN001"],
        min_length=1,
    )
    transactionNumber: str = Field(
        ...,
        description="Unique transaction identifier within the contract",
        examples=["TXN-2024-00123"],
        min_length=1,
    )
    customerName: str = Field(
        ...,
        description="End customer name (may contain special characters requiring Latin-1 encoding)",
        examples=["Müller GmbH", "Société Générale"],
    )
    customerId: str = Field(
        ...,
        description="Unique customer identifier in the vendor system",
        examples=["CUST-DE-4521"],
        min_length=1,
    )
    resellerPartner: Optional[str] = Field(
        default=None,
        description=(
            "Reseller partner identifier. "
            "CRITICAL: If empty or null, IDoc must NOT be created."
        ),
        examples=["PARTNER-EU-789"],
    )
    orderablePartNumber: str = Field(
        ...,
        description="Product part number from the vendor catalog",
        examples=["PROD-LAP-001"],
        min_length=1,
    )
    remainingQuantity: int = Field(
        ...,
        description="Remaining quantity available under this pricing agreement",
        examples=[50],
        ge=0,
    )
    entitledPrice: float = Field(
        ...,
        description="Special entitled price for this product under the agreement",
        examples=[899.99],
        gt=0,
    )
    currency: str = Field(
        ...,
        description="ISO 4217 currency code",
        examples=["EUR", "GBP", "USD"],
        min_length=3,
        max_length=3,
    )
    region: str = Field(
        ...,
        description="Business region code for entity and currency mapping",
        examples=["DACH", "UKI", "NORDICS", "IBERIA"],
    )
    fulfilmentType: str = Field(
        ...,
        description="Fulfillment type (case-insensitive). Valid: 'Dual', 'DUAL', 'Direct', etc.",
        examples=["Dual", "DUAL", "Direct"],
    )
    productBrand: str = Field(
        ...,
        description="Product brand used for hardware vs software/service categorization",
        examples=["Hardware", "Services", "Software"],
    )
    initial: bool = Field(
        ...,
        description=(
            "Processing mode flag for double execution pattern. "
            "True = Phase 1 (create base document), "
            "False = Phase 2 (finalize and activate)."
        ),
        examples=[True, False],
    )

    # Deprecated field — kept for backward compatibility but ignored in logic
    changeFlag: Optional[str] = Field(
        default=None,
        description="DEPRECATED: This field is no longer used in processing logic.",
        deprecated=True,
    )

    # CTO flag — designed for future activation
    ctoFlag: Optional[bool] = Field(
        default=None,
        description=(
            "Configure-to-Order flag. Currently inactive — "
            "designed for future activation without code changes."
        ),
    )

    @field_validator("fulfilmentType")
    @classmethod
    def normalize_fulfilment_type(cls, v: str) -> str:
        """Normalize fulfillment type to uppercase for case-insensitive comparison."""
        return v.strip().upper()

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, v: str) -> str:
        """Normalize currency code to uppercase."""
        return v.strip().upper()

    class Config:
        json_schema_extra = {
            "example": {
                "mcn": "MCN001",
                "transactionNumber": "TXN-2024-00123",
                "customerName": "Müller GmbH",
                "customerId": "CUST-DE-4521",
                "resellerPartner": "PARTNER-EU-789",
                "orderablePartNumber": "PROD-LAP-001",
                "remainingQuantity": 50,
                "entitledPrice": 899.99,
                "currency": "EUR",
                "region": "DACH",
                "fulfilmentType": "Dual",
                "productBrand": "Hardware",
                "initial": True,
            }
        }
