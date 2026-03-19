"""
Unit tests for IDoc generation service.
"""

import pytest
from src.services.idoc_generator import IDocGenerator


@pytest.fixture
def generator():
    return IDocGenerator()


@pytest.fixture
def mapped_fields():
    return {
        "opgan": "MCN001_TXN-001",
        "customer_name": "Test Customer",
        "customer_id": "CUST-001",
        "reseller_partner": "PARTNER-001",
        "orderable_part_number": "PROD-001",
        "remaining_quantity": 50,
        "entitled_price": 899.99,
        "currency": "EUR",
        "region": "DACH",
        "entity_code": "1000",
        "fulfilment_type": "DUAL",
        "product_brand": "Hardware",
        "transaction_type": "ZKE",
        "initial": True,
    }


class TestIDocGenerator:

    def test_generate_initial_mode(self, generator, mapped_fields):
        idoc = generator.generate(
            mapped_fields=mapped_fields,
            opgan="MCN001_TXN-001",
            product_category="Hardware",
            processing_mode="INITIAL",
        )
        assert idoc.header.processing_mode == "INITIAL"
        assert idoc.header.doc_type == "ZSDA"
        assert idoc.header.opgan == "MCN001_TXN-001"
        assert idoc.segment.customer_name == "Test Customer"
        assert idoc.segment.product_category == "Hardware"

    def test_generate_update_mode(self, generator, mapped_fields):
        idoc = generator.generate(
            mapped_fields=mapped_fields,
            opgan="MCN001_TXN-001",
            product_category="Hardware",
            processing_mode="UPDATE",
        )
        assert idoc.header.processing_mode == "UPDATE"

    def test_idoc_id_format(self, generator, mapped_fields):
        idoc = generator.generate(
            mapped_fields=mapped_fields,
            opgan="MCN001_TXN-001",
            product_category="Hardware",
            processing_mode="INITIAL",
        )
        assert idoc.idoc_id.startswith("IDOC-")

    def test_unique_idoc_ids(self, generator, mapped_fields):
        idoc1 = generator.generate(mapped_fields, "O1", "Hardware", "INITIAL")
        idoc2 = generator.generate(mapped_fields, "O2", "Hardware", "INITIAL")
        assert idoc1.idoc_id != idoc2.idoc_id

    def test_get_status(self, generator, mapped_fields):
        idoc = generator.generate(mapped_fields, "O1", "Hardware", "INITIAL")
        status = generator.get_status(idoc.idoc_id)
        assert status is not None
        assert status["status"] == "GENERATED"

    def test_get_status_not_found(self, generator):
        assert generator.get_status("IDOC-NONEXISTENT") is None

    def test_audit_metadata(self, generator, mapped_fields):
        idoc = generator.generate(mapped_fields, "O1", "Hardware", "INITIAL")
        assert "generated_at" in idoc.audit
        assert idoc.audit["processing_mode"] == "INITIAL"
        assert idoc.audit["entity_code"] == "1000"
