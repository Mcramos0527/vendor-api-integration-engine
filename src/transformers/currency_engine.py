"""
Currency logic processing engine.

Handles region-to-currency mappings, multi-currency validation,
and currency-specific formatting rules.
"""

from typing import Dict, Any, Optional

from src.config.loader import ConfigLoader


class CurrencyEngine:
    """
    Processes currency-related business logic.

    Responsibilities:
    - Validate currency against region constraints
    - Resolve default currency for a region
    - Apply decimal formatting rules
    - Handle multi-currency regions
    """

    def __init__(self):
        self.config = ConfigLoader()
        self._currency_rules = self.config.get_all_currency_logic()

    def resolve_currency(self, region: str, currency: str) -> Dict[str, Any]:
        """
        Resolve and validate currency for a given region.

        Returns resolved currency configuration including decimal places
        and whether the currency matches the region default.
        """
        region_config = self._currency_rules.get(region, {})
        default_currency = region_config.get("default_currency", "EUR")
        allowed_currencies = region_config.get("allowed_currencies", [default_currency])

        return {
            "currency_code": currency,
            "is_default": currency == default_currency,
            "is_valid": currency in allowed_currencies,
            "region_default": default_currency,
            "decimal_places": self._get_decimal_places(currency),
        }

    def _get_decimal_places(self, currency: str) -> int:
        """Get the standard decimal places for a currency."""
        # Most currencies use 2 decimal places
        # Notable exceptions
        zero_decimal = {"JPY", "KRW", "VND"}
        three_decimal = {"BHD", "KWD", "OMR"}

        if currency in zero_decimal:
            return 0
        elif currency in three_decimal:
            return 3
        return 2

    def format_price(self, price: float, currency: str) -> str:
        """Format a price according to currency-specific decimal rules."""
        decimal_places = self._get_decimal_places(currency)
        return f"{price:.{decimal_places}f}"
