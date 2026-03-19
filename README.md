# Vendor API Integration Engine

> Enterprise-grade API middleware that transforms vendor catalog data into ERP-compatible documents in near real-time.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Overview

**Vendor API Integration Engine** is a Python middleware service that receives product catalog and special pricing data from external vendor APIs, applies business validation and transformation rules, and generates ERP-compatible Intermediate Documents (IDocs) for automated processing.

Built to handle **multi-region operations** across multiple currencies, regions, and fulfillment models — replacing manual data entry workflows that previously required 40+ hours/week of human effort.

### The Problem

Enterprise distributors receive thousands of special pricing records daily from vendors. These records must be validated, transformed, and loaded into ERP systems to create sales agreements. Manual processing is slow, error-prone, and doesn't scale.

### The Solution

This engine automates the entire pipeline:

```
Vendor JSON Payload → Validation → Transformation → IDoc Generation → ERP Ingestion
```

**Result:** Near real-time processing, zero manual data entry, full audit traceability.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway Layer                      │
│              POST /v1.0/sales/special_bid                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Validation Engine                        │
│  ┌──────────┐ ┌───────────┐ ┌────────────────────┐      │
│  │ Schema   │ │ Composite │ │ Business Rule      │      │
│  │ Validator│ │ Key Check │ │ Validator          │      │
│  └──────────┘ └───────────┘ └────────────────────┘      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Transformation Pipeline                     │
│  ┌──────────┐ ┌───────────┐ ┌────────────────────┐      │
│  │ Field    │ │ Currency  │ │ Product            │      │
│  │ Mapping  │ │ Logic     │ │ Categorization     │      │
│  └──────────┘ └───────────┘ └────────────────────┘      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│               IDoc Generator Service                     │
│         Generates ERP-compatible documents               │
│         with full audit logging                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                     ERP System                           │
│           Sales Agreement / UAN Creation                 │
└─────────────────────────────────────────────────────────┘
```

---

## Key Features

- **REST API Endpoint** — Receives JSON payloads via POST, validates against schema, returns structured responses
- **Composite Key Deduplication** — Prevents duplicate record creation using multi-field composite keys
- **Multi-Region Support** — Handles multiple regions with region-specific currency, tax, and fulfillment rules
- **Configurable Business Rules** — Transaction types, currency mappings, and region tables are externalized as YAML config
- **Double Execution Pattern** — Supports initial/update processing modes for ERP compatibility
- **Character Encoding** — Latin-1 encoding support for international customer names with special characters
- **Product Categorization** — Automatic hardware vs. software/service classification
- **Partner Validation** — Blocks IDoc creation when required partner data is missing
- **Feature Flags** — CTO (Configure-to-Order) flag designed for future activation without code deployment
- **Full Audit Trail** — Every transaction logged with timestamps, validation results, and processing outcomes

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| API Framework | FastAPI |
| Validation | Pydantic v2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Testing | pytest, pytest-asyncio |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Documentation | OpenAPI / Swagger |

---

## Quick Start

### Prerequisites

- Python 3.10+
- pip or poetry

### Installation

```bash
git clone https://github.com/Mcramos0527/vendor-api-integration-engine.git
cd vendor-api-integration-engine

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn src.api.main:app --reload --port 8000
```

### Run Tests

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Docker

```bash
docker build -t vendor-api-engine .
docker run -p 8000:8000 vendor-api-engine
```

---

## API Usage

### Submit a Special Pricing Record

```bash
curl -X POST http://localhost:8000/v1.0/sales/special_bid/by_contract/catalog \
  -H "Content-Type: application/json" \
  -d '{
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
    "initial": true
  }'
```

### Response

```json
{
  "status": "success",
  "idoc_id": "IDOC-2024-07-10-00456",
  "opgan": "MCN001_TXN-2024-00123",
  "product_category": "Hardware",
  "processing_mode": "INITIAL",
  "timestamp": "2024-07-10T14:32:01.123Z"
}
```

### API Docs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Configuration

All business rules are externalized — no code changes needed when rules change.

```
config/
├── transaction_types.yaml    # Maps transaction codes to ERP document types
├── currency_logic.yaml       # Region-to-currency mappings
├── region_mapping.yaml       # Region definitions and entity codes
└── quantity_rules.yaml       # Quantity validation thresholds per product type
```

---

## Project Structure

```
vendor-api-integration-engine/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── routes.py            # API route definitions
│   │   └── middleware.py        # Request logging, error handling
│   ├── models/
│   │   ├── request_models.py    # Pydantic request schemas
│   │   ├── response_models.py   # Pydantic response schemas
│   │   └── idoc_models.py       # IDoc document models
│   ├── validators/
│   │   ├── schema_validator.py  # JSON schema validation
│   │   ├── composite_key.py     # Deduplication logic
│   │   └── business_rules.py    # Business rule validation engine
│   ├── transformers/
│   │   ├── field_mapper.py      # Field mapping and transformation
│   │   ├── currency_engine.py   # Currency logic processing
│   │   └── product_classifier.py # Product categorization
│   ├── services/
│   │   ├── idoc_generator.py    # IDoc document generation
│   │   ├── audit_logger.py      # Audit trail service
│   │   └── duplicate_checker.py # Composite key deduplication
│   ├── config/
│   │   ├── settings.py          # Application settings
│   │   └── loader.py            # YAML configuration loader
│   └── utils/
│       ├── encoding.py          # Character encoding utilities
│       └── feature_flags.py     # Feature flag management
├── tests/
│   ├── test_api.py
│   ├── test_validators.py
│   ├── test_transformers.py
│   ├── test_idoc_generator.py
│   └── test_integration.py
├── config/
│   ├── transaction_types.yaml
│   ├── currency_logic.yaml
│   ├── region_mapping.yaml
│   └── quantity_rules.yaml
├── docs/
│   ├── architecture.md
│   └── configuration.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── LICENSE
```

---

## Business Logic

### Composite Key Deduplication

Each incoming record is checked against a composite key to prevent duplicate ERP documents:

```python
composite_key = hash(mcn, transaction_number, orderable_part_number,
                     remaining_quantity, customer_id, entitled_price)
```

### Double Execution Pattern

The ERP system requires a two-phase commit:
1. **Phase 1 (INITIAL=True)** — Creates the base document structure
2. **Phase 2 (INITIAL=False)** — Finalizes and activates the agreement

### OPGAN Format

The OPGAN identifier follows the format `MCN_TransactionNumber`, serving as the primary business reference for the sales agreement.

### Product Categorization

Products are classified based on brand metadata — `"Services"` and `"Software"` brands map to the Software/Service category; everything else maps to Hardware. This drives downstream document type selection.

---

## Roadmap

- [x] Core API endpoint with FastAPI
- [x] Pydantic validation models
- [x] Composite key deduplication
- [x] Multi-region currency support
- [x] IDoc generation engine
- [x] Audit logging
- [x] Docker containerization
- [x] CI/CD pipeline
- [ ] CTO (Configure-to-Order) flag activation
- [ ] Webhook notifications for processing status
- [ ] Batch processing endpoint for bulk imports
- [ ] Monitoring dashboard integration
- [ ] Redis caching layer for deduplication

---

## Author

**Max Ramos** — Technical Business Analyst & Automation Engineer

- Enterprise systems integration specialist with 10+ years of experience
- Background in ERP environments, REST API integrations, and process automation
- [LinkedIn](https://www.linkedin.com/in/max-ramos-6a1942126) · [GitHub](https://github.com/Mcramos0527)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
