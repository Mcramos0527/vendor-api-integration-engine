"""
Duplicate checking service.

Provides a higher-level interface for deduplication logic,
including batch checking and reporting.
"""

from typing import List, Dict, Any
from src.validators.composite_key import CompositeKeyValidator
from src.models.request_models import SpecialBidRequest


class DuplicateChecker:
    """
    Service layer for duplicate detection.

    Wraps the CompositeKeyValidator with batch operations
    and reporting capabilities.
    """

    def __init__(self, key_validator: CompositeKeyValidator = None):
        self.key_validator = key_validator or CompositeKeyValidator()

    def check_single(self, request: SpecialBidRequest) -> Dict[str, Any]:
        """
        Check a single request for duplicates.

        Returns a report with duplicate status and details.
        """
        composite_key = self.key_validator.generate_key(request)
        is_duplicate = self.key_validator.exists(composite_key)

        report = {
            "composite_key": composite_key[:12] + "...",
            "is_duplicate": is_duplicate,
        }

        if is_duplicate:
            report["existing_idoc_id"] = self.key_validator.get_existing(composite_key)

        return report

    def check_batch(self, requests: List[SpecialBidRequest]) -> Dict[str, Any]:
        """
        Check a batch of requests for duplicates.

        Returns a summary report with counts and individual results.
        """
        results = []
        duplicate_count = 0

        for request in requests:
            result = self.check_single(request)
            results.append(result)
            if result["is_duplicate"]:
                duplicate_count += 1

        return {
            "total_checked": len(requests),
            "duplicates_found": duplicate_count,
            "unique_records": len(requests) - duplicate_count,
            "results": results,
        }

    @property
    def registry_size(self) -> int:
        """Current number of registered composite keys."""
        return self.key_validator.count
