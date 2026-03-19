"""
Unit tests for validators.
"""

import pytest
from src.validators.composite_key import CompositeKeyValidator
from src.validators.business_rules import BusinessRuleValidator
from src.validators.schema_validator import SchemaValidator
from src.models.request_models import SpecialBidRequest


@pytest.fixture
def sample_request():
    return SpecialBidRequest(
        mcn="MCN001",
        transactionNumber="TXN-001",
        customerName="Test Customer",
        customerId="CUST-001",
        resellerPartner="PARTNER-001",
        orderablePartNumber="PROD-001",
        remainingQuantity=10,
        entitledPrice=100.00,
        currency="EUR",
        region="DACH",
        fulfilmentType="DUAL",
        productBrand="Hardware",
        initial=True,
    )


class TestCompositeKeyValidator:

    def test_generate_key_deterministic(self, sample_request):
        """Same request should always produce the same composite key."""
        validator = CompositeKeyValidator()
        key1 = validator.generate_key(sample_request)
        key2 = validator.generate_key(sample_request)
        assert key1 == key2

    def test_different_requests_different_keys(self, sample_request):
        """Different requests should produce different composite keys."""
        validator = CompositeKeyValidator()
        key1 = validator.generate_key(sample_request)

        modified = sample_request.model_copy(update={"remainingQuantity": 999})
        key2 = validator.generate_key(modified)

        assert key1 != key2

    def test_register_and_check(self, sample_request):
        """Registered keys should be found by exists()."""
        validator = CompositeKeyValidator()
        key = validator.generate_key(sample_request)

        assert not validator.exists(key)

        validator.register(key, "IDOC-TEST-001")

        assert validator.exists(key)
        assert validator.get_existing(key) == "IDOC-TEST-001"

    def test_remove_key(self, sample_request):
        """Removed keys should no longer exist."""
        validator = CompositeKeyValidator()
        key = validator.generate_key(sample_request)
        validator.register(key, "IDOC-TEST-002")

        assert validator.remove(key) is True
        assert not validator.exists(key)

    def test_count(self, sample_request):
        validator = CompositeKeyValidator()
        assert validator.count == 0
        key = validator.generate_key(sample_request)
        validator.register(key, "IDOC-001")
        assert validator.count == 1


class TestBusinessRuleValidator:

    def test_valid_request_passes(self, sample_request):
        validator = BusinessRuleValidator()
        result = validator.validate(sample_request)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_null_reseller_fails(self):
        request = SpecialBidRequest(
            mcn="MCN001",
            transactionNumber="TXN-001",
            customerName="Test",
            customerId="CUST-001",
            resellerPartner=None,
            orderablePartNumber="PROD-001",
            remainingQuantity=10,
            entitledPrice=100.00,
            currency="EUR",
            region="DACH",
            fulfilmentType="DUAL",
            productBrand="Hardware",
            initial=True,
        )
        validator = BusinessRuleValidator()
        result = validator.validate(request)
        assert not result.is_valid
        assert any("resellerPartner" in e for e in result.errors)

    def test_mcn_with_underscore_fails(self):
        request = SpecialBidRequest(
            mcn="MCN_INVALID",
            transactionNumber="TXN-001",
            customerName="Test",
            customerId="CUST-001",
            resellerPartner="PARTNER-001",
            orderablePartNumber="PROD-001",
            remainingQuantity=10,
            entitledPrice=100.00,
            currency="EUR",
            region="DACH",
            fulfilmentType="DUAL",
            productBrand="Hardware",
            initial=True,
        )
        validator = BusinessRuleValidator()
        result = validator.validate(request)
        assert not result.is_valid


class TestSchemaValidator:

    def test_valid_payload(self):
        payload = {
            "mcn": "MCN001",
            "transactionNumber": "TXN-001",
            "customerName": "Test",
            "customerId": "CUST-001",
            "orderablePartNumber": "PROD-001",
            "remainingQuantity": 10,
            "entitledPrice": 100.00,
            "currency": "EUR",
            "region": "DACH",
            "fulfilmentType": "Dual",
            "productBrand": "Hardware",
            "initial": True,
        }
        validator = SchemaValidator()
        result = validator.validate(payload)
        assert result.is_valid

    def test_missing_fields_detected(self):
        payload = {"mcn": "MCN001"}
        validator = SchemaValidator()
        result = validator.validate(payload)
        assert not result.is_valid

    def test_deprecated_field_warning(self):
        payload = {
            "mcn": "MCN001",
            "transactionNumber": "TXN-001",
            "customerName": "Test",
            "customerId": "CUST-001",
            "orderablePartNumber": "PROD-001",
            "remainingQuantity": 10,
            "entitledPrice": 100.00,
            "currency": "EUR",
            "region": "DACH",
            "fulfilmentType": "Dual",
            "productBrand": "Hardware",
            "initial": True,
            "changeFlag": "Y",
        }
        validator = SchemaValidator()
        result = validator.validate(payload)
        assert result.is_valid
        assert any("changeFlag" in w for w in result.warnings)
