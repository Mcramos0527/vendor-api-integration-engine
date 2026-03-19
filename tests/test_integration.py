"""
End-to-end integration tests.

Tests the complete pipeline from API request to IDoc generation.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _make_payload(**overrides):
    """Helper to build a payload with optional overrides."""
    base = {
        "mcn": "MCN-INT",
        "transactionNumber": "TXN-INT-001",
        "customerName": "Integration Test Corp",
        "customerId": "CUST-INT-001",
        "resellerPartner": "PARTNER-INT-001",
        "orderablePartNumber": "PROD-INT-001",
        "remainingQuantity": 25,
        "entitledPrice": 499.99,
        "currency": "EUR",
        "region": "DACH",
        "fulfilmentType": "Dual",
        "productBrand": "Hardware",
        "initial": True,
    }
    base.update(overrides)
    return base


class TestDoubleExecutionPattern:
    """Test the double execution pattern (INITIAL + UPDATE)."""

    def test_full_double_execution(self, client):
        """
        Simulate the full double execution pattern:
        1. First call with initial=True creates the base document
        2. Second call with initial=False finalizes it
        """
        # Phase 1: INITIAL
        payload_initial = _make_payload(
            transactionNumber="TXN-DOUBLE-001",
            initial=True,
        )
        resp1 = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=payload_initial,
        )
        assert resp1.status_code == 201
        assert resp1.json()["processing_mode"] == "INITIAL"

        # Phase 2: UPDATE (different composite key due to quantity change)
        payload_update = _make_payload(
            transactionNumber="TXN-DOUBLE-001",
            remainingQuantity=24,  # Changed to avoid duplicate
            initial=False,
        )
        resp2 = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=payload_update,
        )
        assert resp2.status_code == 201
        assert resp2.json()["processing_mode"] == "UPDATE"


class TestMultiRegionProcessing:
    """Test processing across different regions."""

    @pytest.mark.parametrize(
        "region,currency",
        [
            ("DACH", "EUR"),
            ("UKI", "GBP"),
            ("NORDICS", "SEK"),
            ("IBERIA", "EUR"),
        ],
    )
    def test_region_currency_combinations(self, client, region, currency):
        payload = _make_payload(
            transactionNumber=f"TXN-REG-{region}",
            region=region,
            currency=currency,
        )
        resp = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=payload,
        )
        assert resp.status_code == 201


class TestProductCategoryPipeline:
    """Test product categorization through the full pipeline."""

    @pytest.mark.parametrize(
        "brand,expected_category",
        [
            ("Hardware", "Hardware"),
            ("Services", "Software / Service"),
            ("Software", "Software / Service"),
            ("Networking", "Hardware"),
            ("Peripherals", "Hardware"),
        ],
    )
    def test_categorization_end_to_end(self, client, brand, expected_category):
        payload = _make_payload(
            transactionNumber=f"TXN-CAT-{brand}",
            productBrand=brand,
        )
        resp = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=payload,
        )
        assert resp.status_code == 201
        assert resp.json()["product_category"] == expected_category


class TestDeprecatedFields:
    """Test that deprecated fields are accepted but ignored."""

    def test_change_flag_ignored(self, client):
        payload = _make_payload(
            transactionNumber="TXN-DEP-001",
            changeFlag="Y",
        )
        resp = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=payload,
        )
        assert resp.status_code == 201
