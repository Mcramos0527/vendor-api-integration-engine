"""
Configuration file loader.

Loads externalized business rules from YAML configuration files.
This allows business rules to change without code deployments.
"""

import os
from typing import Dict, Any, Set, Optional
from functools import lru_cache

import yaml


class ConfigLoader:
    """
    Loads and caches YAML configuration files for business rules.

    Configuration files include:
    - transaction_types.yaml: ERP document type mappings
    - currency_logic.yaml: Region-to-currency rules
    - region_mapping.yaml: Region definitions and entity codes
    - quantity_rules.yaml: Quantity validation thresholds
    """

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
        )

    @lru_cache(maxsize=None)
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load and cache a YAML configuration file."""
        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._get_defaults(filename)

    def _get_defaults(self, filename: str) -> Dict[str, Any]:
        """Return default configuration when files are not found."""
        defaults = {
            "transaction_types.yaml": {
                "types": {
                    "DUAL": {"erp_type": "ZKE", "description": "Dual fulfillment"},
                    "DIRECT": {"erp_type": "ZKA", "description": "Direct fulfillment"},
                }
            },
            "currency_logic.yaml": {
                "regions": {
                    "DACH": {"default_currency": "EUR", "allowed_currencies": ["EUR"]},
                    "UKI": {"default_currency": "GBP", "allowed_currencies": ["GBP", "EUR"]},
                    "NORDICS": {"default_currency": "EUR", "allowed_currencies": ["EUR", "SEK", "NOK", "DKK"]},
                    "IBERIA": {"default_currency": "EUR", "allowed_currencies": ["EUR"]},
                    "FRANCE": {"default_currency": "EUR", "allowed_currencies": ["EUR"]},
                    "BENELUX": {"default_currency": "EUR", "allowed_currencies": ["EUR"]},
                    "ITALY": {"default_currency": "EUR", "allowed_currencies": ["EUR"]},
                    "EASTERN_EUROPE": {"default_currency": "EUR", "allowed_currencies": ["EUR", "PLN", "CZK", "HUF"]},
                }
            },
            "region_mapping.yaml": {
                "regions": {
                    "DACH": {"entity_code": "1000", "countries": ["DE", "AT", "CH"]},
                    "UKI": {"entity_code": "2000", "countries": ["GB", "IE"]},
                    "NORDICS": {"entity_code": "3000", "countries": ["SE", "NO", "DK", "FI"]},
                    "IBERIA": {"entity_code": "4000", "countries": ["ES", "PT"]},
                    "FRANCE": {"entity_code": "5000", "countries": ["FR"]},
                    "BENELUX": {"entity_code": "6000", "countries": ["NL", "BE", "LU"]},
                    "ITALY": {"entity_code": "7000", "countries": ["IT"]},
                    "EASTERN_EUROPE": {"entity_code": "8000", "countries": ["PL", "CZ", "HU", "RO"]},
                }
            },
            "quantity_rules.yaml": {
                "max_single_order": 99999,
                "min_quantity": 1,
                "bulk_threshold": 1000,
            },
        }
        return defaults.get(filename, {})

    def get_valid_regions(self) -> Set[str]:
        """Get the set of valid region codes."""
        config = self._load_yaml("region_mapping.yaml")
        regions = config.get("regions", {})
        return set(regions.keys())

    def get_valid_currencies(self) -> Set[str]:
        """Get the set of all valid currency codes across regions."""
        config = self._load_yaml("currency_logic.yaml")
        currencies = set()
        for region_config in config.get("regions", {}).values():
            currencies.update(region_config.get("allowed_currencies", []))
        return currencies

    def get_region_mapping(self, region: str) -> Dict[str, Any]:
        """Get the configuration for a specific region."""
        config = self._load_yaml("region_mapping.yaml")
        return config.get("regions", {}).get(region, {})

    def get_currency_logic(self, region: str) -> Dict[str, Any]:
        """Get currency rules for a specific region."""
        config = self._load_yaml("currency_logic.yaml")
        return config.get("regions", {}).get(region, {})

    def get_all_currency_logic(self) -> Dict[str, Any]:
        """Get all currency logic configuration."""
        config = self._load_yaml("currency_logic.yaml")
        return config.get("regions", {})

    def get_transaction_type(self, fulfilment_type: str) -> Dict[str, Any]:
        """Get ERP transaction type mapping for a fulfilment type."""
        config = self._load_yaml("transaction_types.yaml")
        return config.get("types", {}).get(fulfilment_type, {"erp_type": "STANDARD"})

    def get_quantity_rules(self) -> Dict[str, Any]:
        """Get quantity validation rules."""
        return self._load_yaml("quantity_rules.yaml")
