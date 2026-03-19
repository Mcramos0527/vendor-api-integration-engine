"""
Composite key deduplication engine.

Prevents duplicate IDoc creation by maintaining a registry of
composite keys derived from incoming request fields.
"""

import hashlib
from typing import Optional, Dict

from src.models.request_models import SpecialBidRequest
from src.services.audit_logger import audit_logger


class CompositeKeyValidator:
    """
    Generates and tracks composite keys to prevent duplicate ERP documents.

    The composite key is a SHA-256 hash of the following fields:
    - mcn
    - transactionNumber
    - orderablePartNumber
    - remainingQuantity
    - customerId
    - entitledPrice

    In production, this registry would be backed by a database.
    This implementation uses an in-memory store for demonstration.
    """

    def __init__(self):
        # In production: replace with database-backed store
        self._registry: Dict[str, str] = {}

    def generate_key(self, request: SpecialBidRequest) -> str:
        """
        Generate a composite key from the request fields.

        Returns a SHA-256 hash string that uniquely identifies this
        combination of business fields.
        """
        key_components = [
            str(request.mcn),
            str(request.transactionNumber),
            str(request.orderablePartNumber),
            str(request.remainingQuantity),
            str(request.customerId),
            str(request.entitledPrice),
        ]

        raw_key = "|".join(key_components)
        composite_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        audit_logger.debug(
            f"Composite key generated: {composite_key[:12]}... "
            f"from components: {key_components}"
        )

        return composite_key

    def exists(self, composite_key: str) -> bool:
        """Check if a composite key already exists in the registry."""
        return composite_key in self._registry

    def get_existing(self, composite_key: str) -> Optional[str]:
        """Retrieve the IDoc ID associated with an existing composite key."""
        return self._registry.get(composite_key)

    def register(self, composite_key: str, idoc_id: str) -> None:
        """Register a new composite key with its associated IDoc ID."""
        self._registry[composite_key] = idoc_id
        audit_logger.info(
            f"Composite key registered: {composite_key[:12]}... → {idoc_id}"
        )

    def remove(self, composite_key: str) -> bool:
        """Remove a composite key from the registry. Returns True if found."""
        if composite_key in self._registry:
            del self._registry[composite_key]
            return True
        return False

    @property
    def count(self) -> int:
        """Number of registered composite keys."""
        return len(self._registry)
