"""
Unit tests for transformation engines.
"""

import pytest
from src.transformers.product_classifier import ProductClassifier
from src.transformers.field_mapper import FieldMapper
from src.transformers.currency_engine import CurrencyEngine
from src.utils.encoding import encode_customer_name


class TestProductClassifier:

    @pytest.fixture
    def classifier(self):
        return ProductClassifier()

    def test_hardware_classification(self, classifier):
        assert classifier.classify("Hardware") == "Hardware"

    def test_services_classification(self, classifier):
        assert classifier.classify("Services") == "Software / Service"

    def test_software_classification(self, classifier):
        assert classifier.classify("Software") == "Software / Service"

    def test_case_insensitive(self, classifier):
        assert classifier.classify("SERVICES") == "Software / Service"
        assert classifier.classify("services") == "Software / Service"
        assert classifier.classify("SOFTWARE") == "Software / Service"

    def test_unknown_brand_defaults_to_hardware(self, classifier):
        assert classifier.classify("Peripherals") == "Hardware"
        assert classifier.classify("Networking") == "Hardware"

    def test_metadata(self, classifier):
        meta = classifier.get_classification_metadata("Services")
        assert meta["category"] == "Software / Service"
        assert meta["erp_material_type"] == "DIEN"

        meta_hw = classifier.get_classification_metadata("Hardware")
        assert meta_hw["category"] == "Hardware"
        assert meta_hw["erp_material_type"] == "HAWA"


class TestFieldMapper:

    def test_opgan_format(self):
        mapper = FieldMapper()
        opgan = mapper.generate_opgan("MCN001", "TXN-2024-001")
        assert opgan == "MCN001_TXN-2024-001"

    def test_opgan_with_special_mcn(self):
        mapper = FieldMapper()
        opgan = mapper.generate_opgan("MCN999", "TXN-SPECIAL")
        assert opgan == "MCN999_TXN-SPECIAL"


class TestCurrencyEngine:

    @pytest.fixture
    def engine(self):
        return CurrencyEngine()

    def test_eur_decimal_places(self, engine):
        assert engine._get_decimal_places("EUR") == 2

    def test_jpy_zero_decimals(self, engine):
        assert engine._get_decimal_places("JPY") == 0

    def test_bhd_three_decimals(self, engine):
        assert engine._get_decimal_places("BHD") == 3

    def test_format_price_eur(self, engine):
        assert engine.format_price(899.99, "EUR") == "899.99"

    def test_format_price_jpy(self, engine):
        assert engine.format_price(1000, "JPY") == "1000"


class TestEncoding:

    def test_standard_ascii(self):
        assert encode_customer_name("ACME Corp") == "ACME Corp"

    def test_german_characters(self):
        result = encode_customer_name("Müller GmbH")
        assert "Müller" in result

    def test_french_characters(self):
        result = encode_customer_name("Société Générale")
        assert "Société" in result

    def test_empty_string(self):
        assert encode_customer_name("") == ""

    def test_whitespace_trimmed(self):
        assert encode_customer_name("  Test Corp  ") == "Test Corp"
