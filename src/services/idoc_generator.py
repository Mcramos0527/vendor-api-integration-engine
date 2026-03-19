"""
IDoc (Intermediate Document) generation service.

Generates ERP-compatible IDoc documents from transformed
vendor data, ready for ingestion by the ERP system.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

from src.models.idoc_models import IDocDocument, IDocHeader, IDocSegment
from src.services.audit_logger import audit_logger


class IDocGenerator:
    """
    Generates IDoc documents for ERP ingestion.

    The generator creates ZSDA-type IDocs (Sales Agreement Documents)
    with full header and segment data, plus audit metadata.
    """

    def __init__(self):
        # In production: database-backed IDoc registry
        self._idoc_registry: Dict[str, Dict[str, Any]] = {}

    def generate(
        self,
        mapped_fields: Dict[str, Any],
        opgan: str,
        product_category: str,
        processing_mode: str,
    ) -> IDocDocument:
        """
        Generate a complete IDoc document from transformed fields.

        Args:
            mapped_fields: Transformed field dictionary from FieldMapper
            opgan: Generated OPGAN reference
            product_category: Classified product category
            processing_mode: "INITIAL" or "UPDATE"

        Returns:
            Complete IDocDocument ready for ERP ingestion.
        """
        idoc_id = self._generate_idoc_id()

        header = IDocHeader(
            idoc_id=idoc_id,
            doc_type="ZSDA",
            opgan=opgan,
            processing_mode=processing_mode,
            created_at=datetime.now(timezone.utc),
        )

        segment = IDocSegment(
            customer_name=mapped_fields["customer_name"],
            customer_id=mapped_fields["customer_id"],
            reseller_partner=mapped_fields["reseller_partner"],
            orderable_part_number=mapped_fields["orderable_part_number"],
            remaining_quantity=mapped_fields["remaining_quantity"],
            entitled_price=mapped_fields["entitled_price"],
            currency=mapped_fields["currency"],
            region=mapped_fields["region"],
            fulfilment_type=mapped_fields["fulfilment_type"],
            product_category=product_category,
            product_brand=mapped_fields["product_brand"],
        )

        audit = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "processing_mode": processing_mode,
            "entity_code": mapped_fields.get("entity_code", "UNKNOWN"),
            "transaction_type": mapped_fields.get("transaction_type", "STANDARD"),
        }

        idoc = IDocDocument(header=header, segment=segment, audit=audit)

        # Register in the IDoc store
        self._idoc_registry[idoc_id] = {
            "idoc_id": idoc_id,
            "opgan": opgan,
            "status": "GENERATED",
            "product_category": product_category,
            "processing_mode": processing_mode,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        audit_logger.info(f"IDoc generated: {idoc_id} | Type: ZSDA | Mode: {processing_mode}")

        return idoc

    def get_status(self, idoc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the status of a generated IDoc."""
        return self._idoc_registry.get(idoc_id)

    def _generate_idoc_id(self) -> str:
        """Generate a unique IDoc identifier."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        unique = uuid.uuid4().hex[:8].upper()
        return f"IDOC-{timestamp}-{unique}"
