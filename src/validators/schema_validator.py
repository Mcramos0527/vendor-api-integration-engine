"""
JSON schema validation utilities.

Provides additional schema-level validation beyond Pydantic's
built-in validation for edge cases and custom rules.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)


class SchemaValidator:
    """
    Validates raw JSON payloads before Pydantic parsing.

    This catches malformed payloads, unexpected fields, and
    structural issues that Pydantic might not surface clearly.
    """

    REQUIRED_FIELDS = {
        "mcn",
        "transactionNumber",
        "customerName",
        "customerId",
        "orderablePartNumber",
        "remainingQuantity",
        "entitledPrice",
        "currency",
        "region",
        "fulfilmentType",
        "productBrand",
        "initial",
    }

    DEPRECATED_FIELDS = {"changeFlag"}

    def validate(self, payload: Dict[str, Any]) -> SchemaValidationResult:
        """Validate a raw JSON payload against the expected schema."""
        result = SchemaValidationResult()

        # Check for missing required fields
        missing = self.REQUIRED_FIELDS - set(payload.keys())
        if missing:
            result.add_error(f"Missing required fields: {', '.join(sorted(missing))}")

        # Warn about deprecated fields
        deprecated_used = self.DEPRECATED_FIELDS & set(payload.keys())
        for dep_field in deprecated_used:
            result.add_warning(
                f"Field '{dep_field}' is deprecated and will be ignored."
            )

        # Type checks for critical fields
        if "remainingQuantity" in payload:
            if not isinstance(payload["remainingQuantity"], (int, float)):
                result.add_error("remainingQuantity must be a number")

        if "entitledPrice" in payload:
            if not isinstance(payload["entitledPrice"], (int, float)):
                result.add_error("entitledPrice must be a number")

        if "initial" in payload:
            if not isinstance(payload["initial"], bool):
                result.add_error("initial must be a boolean (true/false)")

        return result
