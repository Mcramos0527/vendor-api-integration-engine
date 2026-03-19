"""
Field mapping and transformation engine.

Maps vendor API fields to ERP-compatible field names and formats,
applying transformation rules as needed.
"""

from typing import Dict, Any

from src.models.request_models import SpecialBidRequest
from src.config.loader import ConfigLoader


class FieldMapper:
    """
    Transforms vendor payload fields into ERP-compatible format.

    Responsibilities:
    - Generate OPGAN reference (MCN_TransactionNumber)
    - Map vendor field names to ERP field names
    - Apply formatting rules (encoding, normalization)
    - Resolve region-to-entity mappings
    """

    def __init__(self):
        self.config = ConfigLoader()

    def generate_opgan(self, mcn: str, transaction_number: str) -> str:
        """
        Generate the OPGAN field.

        Format: MCN_TransactionNumber
        This serves as the primary business reference for the sales agreement.
        """
        return f"{mcn}_{transaction_number}"

    def transform(
        self,
        request: SpecialBidRequest,
        encoded_customer_name: str,
    ) -> Dict[str, Any]:
        """
        Transform vendor request fields into ERP-compatible mapped fields.

        Returns a dictionary of mapped fields ready for IDoc generation.
        """
        # Resolve region to entity code
        region_config = self.config.get_region_mapping(request.region)
        entity_code = region_config.get("entity_code", "UNKNOWN")

        # Resolve transaction type
        transaction_config = self.config.get_transaction_type(request.fulfilmentType)

        # Build mapped fields
        mapped = {
            "opgan": self.generate_opgan(request.mcn, request.transactionNumber),
            "customer_name": encoded_customer_name,
            "customer_id": request.customerId,
            "reseller_partner": request.resellerPartner,
            "orderable_part_number": request.orderablePartNumber,
            "remaining_quantity": request.remainingQuantity,
            "entitled_price": request.entitledPrice,
            "currency": request.currency,
            "region": request.region,
            "entity_code": entity_code,
            "fulfilment_type": request.fulfilmentType,
            "product_brand": request.productBrand,
            "transaction_type": transaction_config.get("erp_type", "STANDARD"),
            "initial": request.initial,
        }

        return mapped

    def map_currency(self, region: str, currency: str) -> Dict[str, Any]:
        """
        Map currency based on region logic.

        Some regions have fixed currencies; others allow multiple.
        Returns the resolved currency configuration.
        """
        currency_config = self.config.get_currency_logic(region)

        return {
            "currency_code": currency,
            "decimal_places": currency_config.get("decimal_places", 2),
            "region_default": currency_config.get("default_currency", currency),
        }
