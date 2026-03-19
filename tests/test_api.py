"""
API endpoint tests for the Vendor API Integration Engine.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def valid_payload():
    """Return a valid special bid payload."""
    return {
        "mcn": "MCN001",
        "transactionNumber": "TXN-2024-00123",
        "customerName": "Müller GmbH",
        "customerId": "CUST-DE-4521",
        "resellerPartner": "PARTNER-EU-789",
        "orderablePartNumber": "PROD-LAP-001",
        "remainingQuantity": 50,
        "entitledPrice": 899.99,
        "currency": "EUR",
        "region": "DACH",
        "fulfilmentType": "Dual",
        "productBrand": "Hardware",
        "initial": True,
    }


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestSpecialBidCreation:
    """Tests for the special bid creation endpoint."""

    def test_create_valid_bid(self, client, valid_payload):
        """Test successful IDoc creation with valid payload."""
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["opgan"] == "MCN001_TXN-2024-00123"
        assert data["product_category"] == "Hardware"
        assert data["processing_mode"] == "INITIAL"
        assert "idoc_id" in data
        assert "timestamp" in data

    def test_create_bid_update_mode(self, client, valid_payload):
        """Test IDoc creation in UPDATE mode (initial=False)."""
        valid_payload["initial"] = False
        # Change a field to avoid duplicate
        valid_payload["transactionNumber"] = "TXN-2024-99999"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["processing_mode"] == "UPDATE"

    def test_software_categorization(self, client, valid_payload):
        """Test that 'Services' brand is categorized as Software / Service."""
        valid_payload["productBrand"] = "Services"
        valid_payload["transactionNumber"] = "TXN-SW-001"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201
        assert response.json()["product_category"] == "Software / Service"

    def test_software_brand_categorization(self, client, valid_payload):
        """Test that 'Software' brand is categorized as Software / Service."""
        valid_payload["productBrand"] = "Software"
        valid_payload["transactionNumber"] = "TXN-SW-002"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201
        assert response.json()["product_category"] == "Software / Service"


class TestValidation:
    """Tests for business rule validation."""

    def test_missing_reseller_partner_rejected(self, client, valid_payload):
        """Reseller partner is required — null should be rejected."""
        valid_payload["resellerPartner"] = None
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 422

    def test_empty_reseller_partner_rejected(self, client, valid_payload):
        """Empty string reseller partner should be rejected."""
        valid_payload["resellerPartner"] = ""
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 422

    def test_missing_required_field(self, client, valid_payload):
        """Missing required fields should return 422."""
        del valid_payload["mcn"]
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 422

    def test_negative_price_rejected(self, client, valid_payload):
        """Negative entitled price should be rejected."""
        valid_payload["entitledPrice"] = -10.00
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 422

    def test_zero_price_rejected(self, client, valid_payload):
        """Zero entitled price should be rejected."""
        valid_payload["entitledPrice"] = 0
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 422


class TestDeduplication:
    """Tests for composite key deduplication."""

    def test_duplicate_rejected(self, client, valid_payload):
        """Submitting the same payload twice should return 409 Conflict."""
        # Use unique payload for this test
        valid_payload["transactionNumber"] = "TXN-DUP-TEST-001"

        # First submission should succeed
        response1 = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response1.status_code == 201

        # Second submission with identical data should be rejected
        response2 = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response2.status_code == 409

    def test_different_quantity_not_duplicate(self, client, valid_payload):
        """Different quantity should create a different composite key."""
        valid_payload["transactionNumber"] = "TXN-NODUP-001"

        response1 = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response1.status_code == 201

        valid_payload["remainingQuantity"] = 999
        response2 = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response2.status_code == 201


class TestFulfilmentType:
    """Tests for case-insensitive fulfilment type handling."""

    def test_uppercase_dual(self, client, valid_payload):
        valid_payload["fulfilmentType"] = "DUAL"
        valid_payload["transactionNumber"] = "TXN-FT-001"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201

    def test_mixed_case_dual(self, client, valid_payload):
        valid_payload["fulfilmentType"] = "Dual"
        valid_payload["transactionNumber"] = "TXN-FT-002"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201

    def test_lowercase_dual(self, client, valid_payload):
        valid_payload["fulfilmentType"] = "dual"
        valid_payload["transactionNumber"] = "TXN-FT-003"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201


class TestSpecialCharacters:
    """Tests for Latin-1 character encoding in customer names."""

    def test_german_characters(self, client, valid_payload):
        valid_payload["customerName"] = "Müller & Söhne GmbH"
        valid_payload["transactionNumber"] = "TXN-ENC-001"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201

    def test_french_characters(self, client, valid_payload):
        valid_payload["customerName"] = "Société Générale"
        valid_payload["transactionNumber"] = "TXN-ENC-002"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201

    def test_spanish_characters(self, client, valid_payload):
        valid_payload["customerName"] = "Compañía Ibérica S.L."
        valid_payload["transactionNumber"] = "TXN-ENC-003"
        response = client.post(
            "/v1.0/sales/special_bid/by_contract/catalog",
            json=valid_payload,
        )
        assert response.status_code == 201
