"""
Product categorization engine.

Classifies products as Hardware or Software/Service based on
the productBrand field from the vendor payload.
"""

from typing import Dict


class ProductClassifier:
    """
    Classifies products into categories based on brand metadata.

    Classification rules:
    - If productBrand is "Services" or "Software" → "Software / Service"
    - All other values → "Hardware"

    This categorization drives:
    - ERP document type selection
    - Tax handling rules
    - Fulfillment routing
    """

    SOFTWARE_SERVICE_BRANDS = {"services", "software"}

    CATEGORY_HARDWARE = "Hardware"
    CATEGORY_SOFTWARE_SERVICE = "Software / Service"

    def classify(self, product_brand: str) -> str:
        """
        Classify a product based on its brand value.

        Comparison is case-insensitive.

        Args:
            product_brand: The productBrand value from the vendor payload.

        Returns:
            Product category string: "Hardware" or "Software / Service"
        """
        if product_brand.lower().strip() in self.SOFTWARE_SERVICE_BRANDS:
            return self.CATEGORY_SOFTWARE_SERVICE
        return self.CATEGORY_HARDWARE

    def get_classification_metadata(self, product_brand: str) -> Dict[str, str]:
        """
        Return full classification metadata for a product brand.

        Useful for audit logging and downstream processing.
        """
        category = self.classify(product_brand)

        return {
            "original_brand": product_brand,
            "normalized_brand": product_brand.lower().strip(),
            "category": category,
            "erp_material_type": (
                "DIEN" if category == self.CATEGORY_SOFTWARE_SERVICE else "HAWA"
            ),
        }
