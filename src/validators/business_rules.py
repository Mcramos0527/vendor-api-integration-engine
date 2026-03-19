"""
Business rule validation engine.

Validates incoming requests against configurable business rules
before they enter the transformation pipeline.
"""

from dataclasses import dataclass, field
from typing import List

from src.models.request_models import SpecialBidRequest
from src.config.loader import ConfigLoader


@dataclass
class ValidationResult:
    """Result of business rule validation."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)


class BusinessRuleValidator:
    """
    Validates incoming requests against business rules.

    Rules are applied in sequence. All rules are evaluated
    (not short-circuited) so the caller gets a complete
    list of issues in one pass.
    """

    def __init__(self):
        self.config = ConfigLoader()
        self._valid_regions = self.config.get_valid_regions()
        self._valid_currencies = self.config.get_valid_currencies()
        self._valid_fulfilment_types = {"DUAL", "DIRECT"}

    def validate(self, request: SpecialBidRequest) -> ValidationResult:
        """Run all business rules against the request."""
        result = ValidationResult()

        self._validate_reseller_partner(request, result)
        self._validate_region(request, result)
        self._validate_currency(request, result)
        self._validate_fulfilment_type(request, result)
        self._validate_opgan_format(request, result)
        self._validate_quantity_rules(request, result)

        return result

    def _validate_reseller_partner(
        self, request: SpecialBidRequest, result: ValidationResult
    ):
        """
        Reseller partner is REQUIRED for IDoc creation.
        If empty or null, the IDoc must not be created.
        """
        if not request.resellerPartner or request.resellerPartner.strip() == "":
            result.add_error(
                "resellerPartner is required. IDoc cannot be created without a valid "
                "reseller partner identifier."
            )

    def _validate_region(
        self, request: SpecialBidRequest, result: ValidationResult
    ):
        """Validate that the region code exists in the region configuration."""
        if request.region not in self._valid_regions:
            result.add_error(
                f"Invalid region '{request.region}'. "
                f"Valid regions: {', '.join(sorted(self._valid_regions))}"
            )

    def _validate_currency(
        self, request: SpecialBidRequest, result: ValidationResult
    ):
        """Validate currency code against configured currency logic."""
        if request.currency not in self._valid_currencies:
            result.add_error(
                f"Invalid currency '{request.currency}'. "
                f"Valid currencies: {', '.join(sorted(self._valid_currencies))}"
            )

    def _validate_fulfilment_type(
        self, request: SpecialBidRequest, result: ValidationResult
    ):
        """Validate fulfilment type (already normalized to uppercase by Pydantic)."""
        if request.fulfilmentType not in self._valid_fulfilment_types:
            result.add_error(
                f"Invalid fulfilmentType '{request.fulfilmentType}'. "
                f"Valid types: {', '.join(sorted(self._valid_fulfilment_types))}"
            )

    def _validate_opgan_format(
        self, request: SpecialBidRequest, result: ValidationResult
    ):
        """Validate that MCN and transactionNumber can form a valid OPGAN."""
        if "_" in request.mcn:
            result.add_error(
                "MCN must not contain underscore '_' as it is used as the "
                "OPGAN separator (MCN_TransactionNumber)."
            )

    def _validate_quantity_rules(
        self, request: SpecialBidRequest, result: ValidationResult
    ):
        """Validate quantity against configured thresholds."""
        quantity_rules = self.config.get_quantity_rules()
        max_quantity = quantity_rules.get("max_single_order", 99999)

        if request.remainingQuantity > max_quantity:
            result.add_error(
                f"remainingQuantity ({request.remainingQuantity}) exceeds maximum "
                f"allowed ({max_quantity}). Contact operations for bulk processing."
            )
