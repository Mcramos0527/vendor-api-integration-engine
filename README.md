# Vendor API Integration Engine
 
> Enterprise-grade API middleware that transforms vendor catalog data into ERP-compatible IDoc documents in near real-time — with full WebMethods iPaaS integration architecture.
 
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
 
---
 
## Overview
 
**Vendor API Integration Engine** is a Python middleware service that receives product catalog and special pricing data from external vendor APIs, applies business validation and transformation rules, and generates ERP-compatible Intermediate Documents (IDocs) for automated processing.
 
Built to handle **multi-region operations** across 18+ countries, multiple currencies, and fulfillment models — replacing manual data entry workflows that previously required 40+ hours/week of human effort.
 
> **BA Context:** This project was designed following a real enterprise integration pattern used at TD SYNNEX, where I acted as the Business System Analyst responsible for defining requirements, data flows, error handling specifications, and coordinating delivery between business stakeholders, internal IT, and external vendor technical teams. The architecture reflects decisions made during structured As-Is/To-Be process discovery workshops and stakeholder alignment sessions across EMEA operations.
 
---
 
## The Problem
 
Enterprise distributors receive thousands of special pricing records daily from vendors. These records must be validated, transformed, and loaded into ERP systems to create sales agreements. Manual processing is slow, error-prone, and doesn't scale.
 
| Metric | Before | After |
|---|---|---|
| Processing time per record | 3–5 minutes manual | Near real-time |
| Weekly manual effort | 40+ hours | < 1 hour oversight |
| Error rate | High (manual entry) | Near zero (rule-based) |
| Audit trail | None | Full per-transaction log |
| Region coverage | Single region | 18+ countries, multi-currency |
| Duplicate prevention | Manual check | Composite key deduplication |
 
---
 
## Solution Architecture
 
```
Vendor JSON Payload → Validation → Transformation → IDoc Generation → ERP Ingestion
```
 
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
- **Multi-Region Support** — Handles 18+ countries with region-specific currency, tax, and fulfillment rules
- **Configurable Business Rules** — Transaction types, currency mappings, and region tables externalized as YAML config
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
 
All business rules are externalized — no code changes required when rules change.
 
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
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── routes.py                 # API route definitions
│   │   └── middleware.py             # Request logging, error handling
│   ├── models/
│   │   ├── request_models.py         # Pydantic request schemas
│   │   ├── response_models.py        # Pydantic response schemas
│   │   └── idoc_models.py            # IDoc document models
│   ├── validators/
│   │   ├── schema_validator.py       # JSON schema validation
│   │   ├── composite_key.py          # Deduplication logic
│   │   └── business_rules.py         # Business rule validation engine
│   ├── transformers/
│   │   ├── field_mapper.py           # Field mapping and transformation
│   │   ├── currency_engine.py        # Currency logic processing
│   │   └── product_classifier.py     # Product categorization
│   ├── services/
│   │   ├── idoc_generator.py         # IDoc document generation
│   │   ├── audit_logger.py           # Audit trail service
│   │   └── duplicate_checker.py      # Composite key deduplication
│   ├── config/
│   │   ├── settings.py               # Application settings
│   │   └── loader.py                 # YAML configuration loader
│   └── utils/
│       ├── encoding.py               # Character encoding utilities
│       └── feature_flags.py          # Feature flag management
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
│   ├── configuration.md
│   └── webmethods-integration-spec.md    # iPaaS middleware layer specification
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
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
 
Products are classified based on brand metadata — `"Services"` and `"Software"` brands map to the Software/Service category; everything else maps to Hardware.
 
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
- [ ] WebMethods iPaaS middleware layer *(spec below)*
- [ ] CTO (Configure-to-Order) flag activation
- [ ] Webhook notifications for processing status
- [ ] Batch processing endpoint for bulk imports
- [ ] Redis caching layer for deduplication
- [ ] Monitoring dashboard integration
 
---
 
---
 
# Technical Requirements Specification
## WebMethods iPaaS Integration Layer
### Vendor API Integration Engine — Enterprise Middleware Extension
 
---
 
| Field | Value |
|---|---|
| Document ID | TRS-VAIE-WM-001 |
| Version | 1.0 |
| Author | Max Ramos — Business System Analyst |
| Status | Draft for Stakeholder Review |
| Date | April 2026 |
| Classification | Internal — Technical |
 
---
 
## 1. Purpose & Scope
 
This document defines the technical requirements for introducing **Software AG WebMethods** as an iPaaS (Integration Platform as a Service) middleware layer between the Vendor API Integration Engine and the target ERP system (SAP IDoc ingestion).
 
The current architecture establishes a direct Python FastAPI → ERP pipeline. This specification defines how WebMethods would be inserted as an intermediary to support enterprise-grade message routing, protocol transformation, structured error handling, and multi-system fan-out in production environments.
 
### 1.1 Intended Audience
 
- Business System Analysts reviewing integration architecture
- Enterprise architects evaluating iPaaS platform requirements
- IT delivery teams responsible for WebMethods configuration
- Business stakeholders reviewing future-state integration design
 
### 1.2 Out of Scope
 
- WebMethods server installation and licensing
- SAP Basis configuration for IDoc port setup
- Network firewall and security configuration
- End-user training
 
---
 
## 2. Business Context & Justification
 
The current direct integration pattern works for single-ERP, single-region scenarios. As the vendor integration scales across additional business units, ERP instances, or acquired entities, a direct connection model creates the following risks:
 
| Risk | Impact | Mitigation via WebMethods |
|---|---|---|
| Single point of failure between vendor API and ERP | High | Message queuing and retry logic |
| No protocol abstraction — tight coupling | Medium | WebMethods adapter layer decouples systems |
| No centralised monitoring of integration flows | High | WebMethods IS dashboard |
| Manual intervention required on ERP failures | High | Dead Letter Queue with automatic retry |
| Scaling to new ERP instances requires code changes | Medium | Routing rules managed in WebMethods, not code |
| No standardised error notification | Medium | Event-based alerting via WebMethods |
 
**Business decision:** Insert WebMethods as the enterprise middleware layer to decouple the Vendor API engine from ERP, enabling scalable multi-system routing without modifying core application logic.
 
---
 
## 3. Current State Architecture (As-Is)
 
```
┌─────────────────┐        REST/JSON         ┌──────────────────────┐
│  Vendor API     │ ───────────────────────► │  FastAPI Engine      │
│  (External)     │                          │  (Validation +        │
└─────────────────┘                          │   Transformation)     │
                                             └──────────┬───────────┘
                                                        │ IDoc (flat file)
                                                        ▼
                                             ┌──────────────────────┐
                                             │  SAP ERP             │
                                             │  (IDoc Port)         │
                                             └──────────────────────┘
```
 
**Current limitations:**
- No message persistence — if ERP is unavailable, records are lost
- No retry mechanism on ERP ingestion failure
- No centralised logging or alerting for integration failures
- Tight coupling — any ERP change requires FastAPI code update
 
---
 
## 4. Future State Architecture (To-Be)
 
```
┌─────────────────┐     REST/JSON      ┌──────────────────────┐
│  Vendor API     │ ─────────────────► │  FastAPI Engine      │
│  (External)     │                   │  (Validation +        │
└─────────────────┘                   │   Transformation)     │
                                      └──────────┬────────────┘
                                                 │
                                         Structured payload
                                         (JSON envelope)
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │   WebMethods         │
                                      │   Integration Server │
                                      │                      │
                                      │  ┌────────────────┐  │
                                      │  │ Message Queue  │  │
                                      │  │ (persistent)   │  │
                                      │  └───────┬────────┘  │
                                      │          │           │
                                      │  ┌───────▼────────┐  │
                                      │  │ Routing Engine │  │
                                      │  │ (rules-based)  │  │
                                      │  └───────┬────────┘  │
                                      │          │           │
                                      │  ┌───────▼────────┐  │
                                      │  │ Error Handler  │  │
                                      │  │ + DLQ + Retry  │  │
                                      │  └───────┬────────┘  │
                                      └──────────┼───────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              │                  │                  │
                              ▼                  ▼                  ▼
                     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                     │  SAP ERP     │   │  SAP ERP     │   │  Future ERP  │
                     │  Instance A  │   │  Instance B  │   │  / CRM       │
                     │  (EMEA)      │   │  (APAC)      │   │  (Roadmap)   │
                     └──────────────┘   └──────────────┘   └──────────────┘
```
 
---
 
## 5. Integration Requirements
 
### 5.1 Functional Requirements
 
#### FR-01 — Message Ingestion
The WebMethods Integration Server **must** expose an inbound service endpoint to receive structured payloads from the FastAPI engine via HTTP/S POST.
 
- **Accepted formats:** JSON (primary), XML (fallback)
- **Authentication:** OAuth 2.0 bearer token or mTLS client certificate
- **Endpoint pattern:** `POST /wm/services/vendor/idoc/inbound`
- **Acknowledgement:** Synchronous HTTP 202 Accepted on successful queue entry
 
#### FR-02 — Message Persistence & Queuing
All inbound messages **must** be persisted to a WebMethods message queue before routing begins. No message may be lost due to downstream ERP unavailability.
 
- Queue type: Durable (persisted to disk)
- Message TTL: 72 hours
- Queue capacity: Minimum 50,000 messages
 
#### FR-03 — Routing Engine
WebMethods **must** route messages to the correct ERP instance based on business rules defined in the payload:
 
| Routing Condition | Target |
|---|---|
| `region` = DACH, BENELUX, UK, NORDICS, IBERIA | SAP ERP Instance A (EMEA) |
| `region` = APAC, ANZ | SAP ERP Instance B (APAC) |
| `fulfilmentType` = Dual | Both instances (fan-out) |
| Unknown region | Dead Letter Queue + alert |
 
- Routing rules **must** be configurable without code deployment
- Routing logic **must** be version-controlled in WebMethods IS packages
 
#### FR-04 — Protocol Transformation
WebMethods **must** transform the incoming JSON payload into the SAP IDoc flat-file format required by the target ERP IDoc port.
 
- Source format: JSON (from FastAPI engine)
- Target format: SAP IDoc flat file (ORDERS05 or CREMAS05 depending on transaction type)
- Character encoding: Latin-1 for customer name fields (preserving special characters)
 
#### FR-05 — Error Handling
WebMethods **must** implement structured error handling at each processing stage:
 
| Error Type | Handling |
|---|---|
| Schema validation failure | Reject with 400, log, alert |
| Routing rule not matched | Dead Letter Queue, alert Operations |
| ERP connection timeout | Retry 3x with 30-second backoff, then DLQ |
| ERP IDoc rejection | Log rejection code, alert BA/IT team, DLQ |
| Duplicate detection | Discard silently, log deduplication event |
| Partial fan-out failure | Log partial delivery, retry failed instance only |
 
#### FR-06 — Dead Letter Queue (DLQ)
All unresolvable messages **must** be routed to a Dead Letter Queue with:
 
- Full original payload preserved
- Error classification and timestamp
- Manual reprocessing capability via WebMethods IS console
- Automatic alerting to Operations team on DLQ entry
 
#### FR-07 — Audit Logging
Every message processed through WebMethods **must** generate an audit log entry:
 
```json
{
  "wm_message_id": "WM-2024-07-10-00456",
  "received_at": "2024-07-10T14:32:01.123Z",
  "source": "vendor-api-engine",
  "transaction_number": "TXN-2024-00123",
  "routing_decision": "SAP_EMEA",
  "erp_idoc_id": "IDOC-2024-07-10-00456",
  "processing_status": "DELIVERED",
  "error_code": null,
  "retry_count": 0
}
```
 
---
 
### 5.2 Non-Functional Requirements
 
#### NFR-01 — Performance
- End-to-end processing time: < 30 seconds under normal load
- Peak throughput: Minimum 1,000 messages/hour
- Queue processing latency: < 5 seconds from queue entry to routing start
 
#### NFR-02 — Availability
- WebMethods IS availability: 99.5% uptime
- Planned maintenance: Sundays 02:00–04:00 UTC
- Message queue must persist across WebMethods IS restarts
 
#### NFR-03 — Security
- All inbound connections must use HTTPS/TLS 1.2+
- Authentication required for all inbound service calls
- Audit logs retained for minimum 12 months
- No PII stored in message queue beyond TTL
 
#### NFR-04 — Scalability
- Architecture must support addition of new ERP routing targets without core changes
- Routing rules must be externally configurable (no code deployment required)
 
---
 
## 6. Data Flow Specification
 
### 6.1 Inbound Payload (FastAPI → WebMethods)
 
```json
{
  "wm_envelope": {
    "source_system": "vendor-api-engine",
    "message_version": "1.0",
    "sent_at": "2024-07-10T14:32:00.000Z",
    "correlation_id": "MCN001_TXN-2024-00123"
  },
  "business_payload": {
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
    "initial": true,
    "idoc_id": "IDOC-2024-07-10-00456"
  }
}
```
 
### 6.2 Field Mapping — JSON to SAP IDoc (ORDERS05)
 
| Source Field (JSON) | IDoc Segment | IDoc Field | Transformation |
|---|---|---|---|
| `mcn` | E1EDK01 | BELNR | Direct |
| `transactionNumber` | E1EDK01 | IHREZ | Direct |
| `customerName` | E1EDKA1 | NAME1 | Latin-1 encode |
| `customerId` | E1EDKA1 | PARTN | Direct |
| `resellerPartner` | E1EDKA1 | PARTN (role RE) | Direct |
| `orderablePartNumber` | E1EDP01 | MATNR | Direct |
| `remainingQuantity` | E1EDP01 | MENGE | Cast to decimal |
| `entitledPrice` | E1EDP01 | PREIS | Cast to decimal |
| `currency` | E1EDK01 | CURCY | ISO 4217 lookup |
| `region` | E1EDK01 | REGIO | Region table lookup |
| `fulfilmentType` | E1EDK01 | BSART | Fulfilment type mapping |
| `initial` | Control Record | DIRECT | 1=INITIAL, 0=UPDATE |
 
### 6.3 Trigger & Event Definitions
 
| Trigger | Event | Action |
|---|---|---|
| Inbound POST received | `MESSAGE_RECEIVED` | Queue entry created |
| Routing rule matched | `ROUTING_RESOLVED` | Forward to ERP adapter |
| ERP IDoc accepted | `DELIVERY_CONFIRMED` | Audit log: DELIVERED |
| ERP returns error | `ERP_REJECTION` | DLQ entry + alert |
| Retry limit exceeded | `MAX_RETRY_EXCEEDED` | DLQ entry + escalation |
| DLQ entry created | `DLQ_ENTRY` | Email alert to Operations |
| Duplicate detected | `DUPLICATE_DISCARDED` | Audit log: DISCARDED |
 
---
 
## 7. Acceptance Criteria
 
| ID | Criterion | Test Method |
|---|---|---|
| AC-01 | All inbound messages queued within 2 seconds | Load test: 100 msg/min |
| AC-02 | DACH region payload routes to EMEA ERP | Integration test |
| AC-03 | Dual fulfilment delivers to both ERP instances | Integration test, verify both IDoc ports |
| AC-04 | ERP timeout triggers 3x retry before DLQ | Simulate ERP downtime |
| AC-05 | DLQ entry triggers Operations alert within 60s | Manual DLQ injection |
| AC-06 | Duplicate composite key discarded, no ERP delivery | Submit identical payload twice |
| AC-07 | All transactions in audit log with correct fields | Audit log query after test batch |
| AC-08 | Routing rules updated without redeployment | Update config, verify new routing |
| AC-09 | Latin-1 names preserved (Ä, Ö, Ü, ñ) | Test payload with special characters |
| AC-10 | 1,000 messages processed within 1 hour | Load test with synthetic data |
 
---
 
## 8. Open Items & Decisions Required
 
| ID | Item | Owner |
|---|---|---|
| OI-01 | Confirm WebMethods IS version in target environment | IT Infrastructure |
| OI-02 | Confirm SAP IDoc port configuration for EMEA instance | SAP Basis team |
| OI-03 | Agree OAuth 2.0 vs mTLS for inbound authentication | Security team |
| OI-04 | Confirm DLQ alert distribution list | Business Owner |
| OI-05 | Confirm APAC ERP IDoc port availability | SAP Basis team |
| OI-06 | Define retention policy for WebMethods audit logs | Compliance / Legal |
 
---
 
## 9. Glossary
 
| Term | Definition |
|---|---|
| iPaaS | Integration Platform as a Service — middleware for connecting enterprise systems |
| WebMethods IS | Software AG WebMethods Integration Server |
| IDoc | Intermediate Document — SAP's standard asynchronous data exchange format |
| DLQ | Dead Letter Queue — holding queue for unprocessable messages |
| Fan-out | Delivering one message to multiple target systems simultaneously |
| mTLS | Mutual TLS — two-way certificate-based authentication |
| OPGAN | Business reference: MCN_TransactionNumber |
| Composite Key | Unique record identifier derived from multiple business fields |
| TTL | Time to Live — maximum message persistence time in queue |
 
---
 
## Author
 
**Max Ramos** — Technical Business Analyst & Automation Engineer
 
Enterprise systems integration specialist with 10+ years across SAP environments, REST API integrations, middleware coordination, and process automation across EMEA.
 
- [LinkedIn](https://www.linkedin.com/in/max-ramos-6a1942126)
- [GitHub](https://github.com/Mcramos0527)
- [Portfolio](https://mcramos0527.github.io/maxramos)
 
---
 
## License
 
MIT License — see [LICENSE](LICENSE) for details.
