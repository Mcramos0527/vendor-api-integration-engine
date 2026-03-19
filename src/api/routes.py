"""
API route definitions for the Vendor API Integration Engine.
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from src.models.request_models import SpecialBidRequest
from src.models.response_models import (
    SpecialBidResponse,
    ErrorResponse,
    DuplicateResponse,
)
from src.validators.business_rules import BusinessRuleValidator
from src.validators.composite_key import CompositeKeyValidator
from src.transformers.field_mapper import FieldMapper
from src.transformers.product_classifier import ProductClassifier
from src.services.idoc_generator import IDocGenerator
from src.services.audit_logger import audit_logger
from src.utils.encoding import encode_customer_name

router = APIRouter(prefix="/v1.0/sales", tags=["Special Bid Processing"])

# Initialize services
business_validator = BusinessRuleValidator()
composite_key_validator = CompositeKeyValidator()
field_mapper = FieldMapper()
product_classifier = ProductClassifier()
idoc_generator = IDocGenerator()


@router.post(
    "/special_bid/by_contract/catalog",
    response_model=SpecialBidResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": DuplicateResponse, "description": "Duplicate record detected"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
    summary="Submit a special bid record for ERP processing",
    description=(
        "Receives a vendor special pricing record, validates it against business rules, "
        "transforms the data, and generates an ERP-compatible IDoc document."
    ),
)
async def create_special_bid(request: SpecialBidRequest):
    """
    Process a special bid record through the integration pipeline.

    Pipeline stages:
    1. Business rule validation (partner check, field validation)
    2. Composite key deduplication check
    3. Field transformation and mapping
    4. Product categorization
    5. IDoc generation
    6. Audit logging
    """
    request_id = f"REQ-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    audit_logger.info(f"[{request_id}] Processing special bid request")

    # --- Stage 1: Business Rule Validation ---
    validation_result = business_validator.validate(request)
    if not validation_result.is_valid:
        audit_logger.warning(
            f"[{request_id}] Validation failed: {validation_result.errors}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "status": "validation_error",
                "errors": validation_result.errors,
                "request_id": request_id,
            },
        )

    # --- Stage 2: Deduplication Check ---
    composite_key = composite_key_validator.generate_key(request)
    if composite_key_validator.exists(composite_key):
        existing_idoc = composite_key_validator.get_existing(composite_key)
        audit_logger.info(
            f"[{request_id}] Duplicate detected. Existing IDoc: {existing_idoc}"
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "duplicate",
                "message": "Record with identical composite key already exists",
                "existing_idoc_id": existing_idoc,
                "composite_key": composite_key,
                "request_id": request_id,
            },
        )

    # --- Stage 3: Field Transformation ---
    encoded_customer_name = encode_customer_name(request.customerName)
    opgan = field_mapper.generate_opgan(request.mcn, request.transactionNumber)
    mapped_fields = field_mapper.transform(request, encoded_customer_name)

    # --- Stage 4: Product Categorization ---
    product_category = product_classifier.classify(request.productBrand)

    # --- Stage 5: IDoc Generation ---
    processing_mode = "INITIAL" if request.initial else "UPDATE"
    idoc = idoc_generator.generate(
        mapped_fields=mapped_fields,
        opgan=opgan,
        product_category=product_category,
        processing_mode=processing_mode,
    )

    # --- Stage 6: Register composite key and log ---
    composite_key_validator.register(composite_key, idoc.idoc_id)

    audit_logger.info(
        f"[{request_id}] IDoc generated successfully: {idoc.idoc_id} "
        f"| OPGAN: {opgan} | Mode: {processing_mode} | Category: {product_category}"
    )

    return SpecialBidResponse(
        status="success",
        idoc_id=idoc.idoc_id,
        opgan=opgan,
        product_category=product_category,
        processing_mode=processing_mode,
        timestamp=datetime.now(timezone.utc),
        request_id=request_id,
    )


@router.get(
    "/special_bid/status/{idoc_id}",
    summary="Check IDoc processing status",
)
async def get_idoc_status(idoc_id: str):
    """Retrieve the processing status of a generated IDoc."""
    idoc_record = idoc_generator.get_status(idoc_id)
    if not idoc_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"status": "not_found", "message": f"IDoc {idoc_id} not found"},
        )
    return idoc_record


@router.get(
    "/special_bid/audit/{request_id}",
    summary="Retrieve audit trail for a request",
)
async def get_audit_trail(request_id: str):
    """Retrieve the complete audit trail for a processing request."""
    trail = audit_logger.get_trail(request_id)
    if not trail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "not_found",
                "message": f"No audit trail found for {request_id}",
            },
        )
    return {"request_id": request_id, "audit_entries": trail}
