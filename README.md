# Vendor API Integration Engine
 
> Enterprise-grade API middleware implementing a full Ship & Debit vendor pricing pipeline — from external vendor API through WebMethods iPaaS, SAP IDoc ingestion, ZO_SD_LIST price list creation, and Unique Approval Number (UAN) generation.
 
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)
[![WebMethods](https://img.shields.io/badge/iPaaS-WebMethods-orange.svg)]()
[![SAP IDoc](https://img.shields.io/badge/SAP-IDoc%20Integration-blue.svg)]()
 
---
 
## Table of Contents
 
- [Overview](#overview)
- [Business Context — Ship & Debit](#business-context--ship--debit)
- [End-to-End Integration Flow](#end-to-end-integration-flow)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Business Logic](#business-logic)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [WebMethods iPaaS — Technical Requirements Specification](#webmethods-ipaas--technical-requirements-specification)
---
 
## Overview
 
**Vendor API Integration Engine** is the application layer within a full enterprise Ship & Debit pricing pipeline. It receives special pricing records from external vendor APIs, applies validation and transformation rules, and delivers structured IDoc payloads to **WebMethods Integration Server** — which routes them into SAP for backend price list creation, Unique Approval Number (UAN) generation, and IDoc status confirmation via WE02.
 
Built to handle **multi-region enterprise operations** across 18+ countries, multiple currencies, and fulfillment models — eliminating 40+ hours/week of manual ERP data entry across EMEA.
 
> **BA Context**
>
> This project was designed following a real enterprise integration pattern delivered at **TD SYNNEX**, where I acted as the **Business System Analyst** responsible for:
> - Defining the end-to-end integration requirements across vendor API, WebMethods, SAP SD, and IDoc layers
> - Facilitating As-Is / To-Be process discovery workshops with EMEA Finance, Sales Operations, and IT stakeholders
> - Documenting field mapping specifications, trigger logic, error handling, and acceptance criteria for engineering handoff
> - Coordinating delivery between internal IT, SAP Basis team, and external vendor technical teams
> - Defining the ZO_SD_LIST price list creation logic and UAN generation business rules
>
> The architecture and WebMethods specification reflect real decisions made in a production enterprise environment supporting Ship & Debit operations across EMEA.
 
---
 
## Business Context — Ship & Debit
 
### What is Ship & Debit?
 
Ship & Debit is a vendor pricing program used widely in technology distribution. The flow works as follows:
 
1. A **vendor** (e.g. Lenovo, HP) agrees to offer a special price to a specific end customer through a distributor (e.g. TD SYNNEX)
2. The distributor **ships the product at standard price** to the reseller
3. After shipment, the distributor **claims the difference** (the "debit") back from the vendor based on the approved special price
4. The claim is only valid if a **Unique Approval Number (UAN)** exists in SAP — created from the vendor's pricing record
Without automation, every pricing record had to be manually entered into SAP to create the UAN. This process was the bottleneck.
 
### Impact Before vs. After
 
| Metric | Before | After |
|---|---|---|
| Processing time per record | 3–5 min manual | Near real-time |
| Weekly manual effort | **40+ hours** | < 1 hour oversight |
| Error rate | High (manual entry) | Near zero (rule-based) |
| Audit trail | None | Full per-transaction log |
| Region coverage | Single region | **18+ countries, multi-currency** |
| Duplicate UAN prevention | Manual check | Composite key deduplication |
| ERP failure handling | Data loss | Retry + Dead Letter Queue |
| IDoc visibility | Phone calls to SAP Basis | WE02 real-time monitoring |
 
---
 
## End-to-End Integration Flow
 
This is the complete pipeline from vendor pricing record to SAP UAN creation:
 
```
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1 — Vendor API                                                  │
│  External vendor (Lenovo, HP, etc.) sends special pricing record      │
│  via REST API — JSON payload with customer, product, price, region    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  POST /v1.0/sales/special_bid
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 2 — FastAPI Application Engine                                  │
│  Receives JSON payload                                                │
│  ├── Schema validation (Pydantic v2)                                 │
│  ├── Composite key deduplication check                               │
│  ├── Business rule validation (region, currency, partner)            │
│  ├── Field mapping & transformation                                  │
│  ├── Product categorisation (Hardware / Software / Service)          │
│  └── Structured IDoc envelope generation                             │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  Structured JSON envelope
                               │  POST → WebMethods inbound service
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 3 — WebMethods Integration Server (iPaaS layer)                 │
│  ├── Message ingestion & durable queue persistence                   │
│  ├── Routing engine → determines target SAP instance by region       │
│  ├── Protocol transformation → JSON to SAP IDoc flat-file            │
│  ├── Error handling → retry logic, Dead Letter Queue                 │
│  └── Audit logging per message                                       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  SAP IDoc (ORDERS05 / custom Z-type)
                               │  delivered to SAP IDoc port
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 4 — SAP IDoc Ingestion                                          │
│  IDoc received and processed by SAP                                  │
│  ├── IDoc type: ORDERS05 or Z-custom Ship & Debit type               │
│  └── Triggers ZO_SD_LIST backend price list processing               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  IDoc processing triggers
                               │  SAP SD backend transaction
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 5 — ZO_SD_LIST (SAP Custom Transaction)                         │
│  Backend Ship & Debit price list creation                            │
│  ├── Applies vendor special price to customer/product/region         │
│  ├── Validates pricing against SAP SD conditions                     │
│  ├── Generates Unique Approval Number (UAN)                          │
│  └── UAN is the authorisation reference for Ship & Debit claims      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  UAN created
                               │  IDoc status updated
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 6 — WE02 (SAP IDoc Monitoring Transaction)                      │
│  Operations & BA team monitor IDoc delivery status                   │
│  ├── Status 53 = IDoc posted successfully → UAN created              │
│  ├── Status 51 = Application error → review required                 │
│  ├── Status 64 = IDoc ready to be transferred                        │
│  └── Full IDoc content visible — header, segments, status history    │
└──────────────────────────────────────────────────────────────────────┘
```
 
---
 
## Key Features
 
| Feature | Description |
|---|---|
| Full Ship & Debit Pipeline | End-to-end automation from vendor API to SAP UAN generation |
| WebMethods iPaaS Layer | Enterprise middleware for routing, transformation, and error handling |
| REST API Endpoint | POST endpoint receives JSON payloads, validates, returns structured responses |
| Composite Key Deduplication | Prevents duplicate UAN creation using multi-field composite keys |
| Multi-Region Support | 18+ countries — region-specific currency, tax, and fulfillment rules |
| Configurable Business Rules | YAML-externalized rules — no code deployment needed when rules change |
| Double Execution Pattern | Initial/update processing modes for SAP IDoc two-phase commit |
| Character Encoding | Latin-1 support for international customer names (Ä, Ö, Ü, ñ) |
| Product Categorization | Automatic hardware vs. software/service classification |
| Partner Validation | Blocks IDoc creation when required partner data is missing |
| WE02 Visibility | All IDoc statuses visible in SAP WE02 for operations monitoring |
| Full Audit Trail | Every transaction logged — timestamp, validation result, UAN reference |
 
---
 
## Tech Stack
 
| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core application runtime |
| API Framework | FastAPI | REST endpoint, OpenAPI docs, async support |
| Validation | Pydantic v2 | Schema validation and type safety |
| **iPaaS / Middleware** | **WebMethods Integration Server** | **Message routing, IDoc transformation, retry logic** |
| **ERP** | **SAP ECC 6.0** | **IDoc ingestion, ZO_SD_LIST, UAN generation** |
| **IDoc Monitoring** | **SAP WE02** | **IDoc status visibility and troubleshooting** |
| Database | SQLite (dev) / PostgreSQL (prod) | Audit log persistence |
| Testing | pytest, pytest-asyncio | Unit and integration tests |
| CI/CD | GitHub Actions | Automated test and build pipeline |
| Containerization | Docker | Environment consistency |
| Documentation | OpenAPI / Swagger | Auto-generated API docs |
 
---
 
## Quick Start
 
### Prerequisites
 
- Python 3.10+
- pip or poetry
- Docker (optional)
### Installation
 
```bash
git clone https://github.com/Mcramos0527/vendor-api-integration-engine.git
cd vendor-api-integration-engine
 
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
 
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
 
## Business Logic
 
### Ship & Debit — UAN Creation Flow
 
The Unique Approval Number (UAN) is the core business output of this pipeline. It is the reference that authorises the distributor to claim the price difference from the vendor after shipment.
 
```
Vendor sends special price → IDoc created → ZO_SD_LIST processes price list
→ UAN generated in SAP → Distributor ships at standard price
→ Distributor claims debit using UAN reference → Vendor reimburses difference
```
 
A UAN is only valid if:
- The IDoc was successfully posted in SAP (WE02 status 53)
- The composite key is unique — no duplicate UAN for the same customer/product/price
- The partner reference is valid — reseller exists in SAP as a registered partner
- The pricing record falls within the active validity period
### Composite Key Deduplication
 
Each incoming record is checked against a composite key to prevent duplicate UAN creation:
 
```python
composite_key = hash(mcn, transaction_number, orderable_part_number,
                     remaining_quantity, customer_id, entitled_price)
```
 
If a duplicate is detected, the record is discarded silently and logged — no IDoc is created and no UAN is generated.
 
### Double Execution Pattern
 
SAP IDoc processing for Ship & Debit requires a two-phase commit:
1. **Phase 1 (INITIAL=True)** — Creates the base IDoc and price list structure in ZO_SD_LIST
2. **Phase 2 (INITIAL=False)** — Finalises and activates the UAN
### WE02 Status Reference
 
After IDoc delivery, operations teams monitor status in SAP transaction WE02:
 
| WE02 Status | Code | Meaning | Action Required |
|---|---|---|---|
| Posted successfully | 53 | IDoc processed — UAN created | None |
| Application error | 51 | SAP rejected IDoc — logic error | BA/IT review required |
| Ready to transfer | 64 | IDoc queued for processing | Monitor |
| Error in WebMethods | 26 | Delivery failed at middleware | WebMethods DLQ review |
 
### OPGAN Format
 
The OPGAN identifier follows the format `MCN_TransactionNumber`, serving as the primary cross-system reference linking the vendor API record to the SAP UAN.
 
### Product Categorization
 
Products are classified based on brand metadata — `"Services"` and `"Software"` brands map to the Software/Service IDoc type; everything else maps to Hardware. This drives the downstream SAP document type selection in ZO_SD_LIST.
 
---
 
## Configuration
 
All business rules are externalized — no code changes required when rules change.
 
```
config/
├── transaction_types.yaml    # Maps transaction codes to SAP document types
├── currency_logic.yaml       # Region-to-currency mappings
├── region_mapping.yaml       # Region definitions and SAP entity codes
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
│   ├── ship-and-debit-flow.md
│   ├── uan-creation-logic.md
│   ├── we02-monitoring-guide.md
│   └── webmethods-integration-spec.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── LICENSE
```
 
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
- [ ] WebMethods iPaaS middleware layer *(full spec below)*
- [ ] CTO (Configure-to-Order) flag activation
- [ ] Webhook notifications for WE02 status updates
- [ ] Batch processing endpoint for bulk Ship & Debit imports
- [ ] Redis caching layer for deduplication
- [ ] Monitoring dashboard — real-time UAN creation rate and IDoc status
---
 
---
 
# Technical Requirements Specification
## WebMethods iPaaS Integration Layer
### Vendor API Integration Engine — Ship & Debit Pipeline
 
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
 
## TRS-1 · Purpose & Scope
 
This document defines the technical requirements for **Software AG WebMethods Integration Server** as the iPaaS middleware layer within the Ship & Debit vendor pricing pipeline.
 
WebMethods sits between the FastAPI application engine and the SAP ERP system, responsible for:
- Receiving structured IDoc envelopes from the FastAPI engine
- Persisting messages to a durable queue
- Routing messages to the correct SAP instance based on region
- Transforming JSON payloads into SAP IDoc flat-file format
- Handling errors, retries, and Dead Letter Queue management
- Delivering IDocs to SAP for ZO_SD_LIST processing and UAN creation
- Providing audit logging for every message processed
### 1.1 Intended Audience
 
- Business System Analysts reviewing integration architecture
- Enterprise architects evaluating iPaaS platform requirements
- IT delivery teams responsible for WebMethods configuration
- SAP Basis team responsible for IDoc port setup
- Business stakeholders reviewing Ship & Debit automation design
### 1.2 Out of Scope
 
- WebMethods server installation and licensing
- SAP Basis configuration for IDoc port setup and ZO_SD_LIST
- Network firewall and security configuration
- End-user training on WE02 monitoring
---
 
## TRS-2 · Business Context & Justification
 
The Ship & Debit pipeline requires reliable, traceable delivery of pricing records into SAP to generate UANs. Without a middleware layer, the following risks exist:
 
| Risk | Business Impact | Mitigation via WebMethods |
|---|---|---|
| ERP unavailability causes pricing record loss | UAN not created — Ship & Debit claim invalid | Durable message queue with 72h TTL |
| No retry on IDoc delivery failure | Manual re-entry required — 40+ hours/week resurfaces | Automatic retry with backoff |
| No centralised monitoring of integration failures | Blind spot — errors discovered only when claims are rejected | WebMethods IS dashboard + WE02 integration |
| Tight coupling — SAP change requires code update | High maintenance cost | WebMethods adapter decouples systems |
| Single SAP instance — cannot scale to APAC | Business expansion blocked | Rules-based multi-instance routing |
| No standardised error alerting | Operations team discovers failures reactively | Event-based DLQ alerting |
 
---
 
## TRS-3 · Current State Architecture (As-Is)
 
```
┌─────────────────┐     REST/JSON      ┌──────────────────────┐
│  Vendor API     │ ─────────────────► │  FastAPI Engine      │
│  (External)     │                   │  Validation +         │
└─────────────────┘                   │  Transformation       │
                                      └──────────┬────────────┘
                                                 │
                                           IDoc flat-file
                                           (direct delivery)
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │  SAP ECC 6.0         │
                                      │  IDoc Port           │
                                      │  ZO_SD_LIST          │
                                      │  UAN Creation        │
                                      └──────────────────────┘
```
 
**Limitations of current state:**
- No message persistence — ERP downtime = data loss
- No retry mechanism on IDoc delivery failure
- No multi-instance routing capability
- No centralised integration monitoring
- Tight coupling between FastAPI and SAP
---
 
## TRS-4 · Future State Architecture (To-Be)
 
```
┌─────────────────┐     REST/JSON      ┌──────────────────────────────┐
│  Vendor API     │ ─────────────────► │  FastAPI Engine              │
│  (External)     │                   │  Validation + Transformation  │
└─────────────────┘                   └──────────────┬───────────────┘
                                                     │
                                          Structured JSON envelope
                                          POST → WebMethods inbound
                                                     │
                                                     ▼
                              ┌──────────────────────────────────────┐
                              │     WebMethods Integration Server     │
                              │                                       │
                              │  ┌─────────────────────────────────┐  │
                              │  │  Inbound Service                │  │
                              │  │  POST /wm/services/vendor/      │  │
                              │  │       idoc/inbound              │  │
                              │  └────────────────┬────────────────┘  │
                              │                   │                   │
                              │  ┌────────────────▼────────────────┐  │
                              │  │  Durable Message Queue          │  │
                              │  │  (72h TTL · 50k capacity)       │  │
                              │  └────────────────┬────────────────┘  │
                              │                   │                   │
                              │  ┌────────────────▼────────────────┐  │
                              │  │  Routing Engine                 │  │
                              │  │  Region → SAP Instance mapping  │  │
                              │  │  Fan-out for Dual fulfilment     │  │
                              │  └────────────────┬────────────────┘  │
                              │                   │                   │
                              │  ┌────────────────▼────────────────┐  │
                              │  │  Protocol Transformer           │  │
                              │  │  JSON → SAP IDoc flat-file      │  │
                              │  │  Field mapping · Latin-1 encode │  │
                              │  └────────────────┬────────────────┘  │
                              │                   │                   │
                              │  ┌────────────────▼────────────────┐  │
                              │  │  Error Handler                  │  │
                              │  │  Retry 3x · DLQ · Alerting      │  │
                              │  └────────────────┬────────────────┘  │
                              └───────────────────┼───────────────────┘
                                                  │
                         ┌────────────────────────┼────────────────────────┐
                         │                        │                        │
                         ▼                        ▼                        ▼
              ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
              │  SAP ECC        │      │  SAP ECC        │      │  Future ERP     │
              │  Instance A     │      │  Instance B     │      │  / CRM          │
              │  EMEA           │      │  APAC           │      │  (Roadmap)      │
              │                 │      │                 │      └─────────────────┘
              │  IDoc Port      │      │  IDoc Port      │
              │  ZO_SD_LIST     │      │  ZO_SD_LIST     │
              │  UAN Creation   │      │  UAN Creation   │
              │  WE02 Monitor   │      │  WE02 Monitor   │
              └─────────────────┘      └─────────────────┘
```
 
---
 
## TRS-5 · Functional Requirements
 
### FR-01 · Message Ingestion `[MUST]`
 
WebMethods Integration Server must expose an inbound service endpoint to receive structured IDoc envelopes from the FastAPI engine.
 
| Parameter | Specification |
|---|---|
| Protocol | HTTPS |
| Method | POST |
| Endpoint | `/wm/services/vendor/idoc/inbound` |
| Accepted format | JSON (primary) · XML (fallback) |
| Authentication | OAuth 2.0 bearer token or mTLS client certificate |
| Acknowledgement | HTTP 202 Accepted — synchronous, on successful queue entry |
| Rejection response | HTTP 400 — schema failure · HTTP 401 — authentication failure |
 
---
 
### FR-02 · Message Persistence & Queuing `[MUST]`
 
All inbound messages must be persisted to a durable queue before routing begins. No message may be lost due to downstream SAP unavailability.
 
| Parameter | Specification |
|---|---|
| Queue type | Durable (disk-persisted) |
| Message TTL | 72 hours |
| Minimum capacity | 50,000 messages |
| Persistence across restart | Required |
| Queue ordering | FIFO per region |
 
---
 
### FR-03 · Routing Engine `[MUST]`
 
WebMethods must route messages to the correct SAP ECC instance based on business rules defined in the payload.
 
| Region Value | Target SAP Instance |
|---|---|
| DACH, BENELUX, UK, NORDICS, IBERIA | SAP ECC Instance A — EMEA |
| APAC, ANZ | SAP ECC Instance B — APAC |
| `fulfilmentType = Dual` | Fan-out → both instances |
| Unknown / unmatched region | Dead Letter Queue + Operations alert |
 
- Routing rules must be configurable **without code deployment**
- Rules must be version-controlled in WebMethods IS packages
- New routing targets must be addable without modifying core pipeline
---
 
### FR-04 · Protocol Transformation `[MUST]`
 
WebMethods must transform the incoming JSON envelope into the SAP IDoc flat-file format required by the target SAP IDoc port.
 
| Parameter | Specification |
|---|---|
| Source format | JSON (structured envelope from FastAPI) |
| Target format | SAP IDoc flat-file |
| IDoc type — Hardware | ORDERS05 |
| IDoc type — Software/Service | Z-custom Ship & Debit type |
| Character encoding | Latin-1 (customer name fields) |
| Field mapping reference | TRS-7.2 field mapping table |
 
---
 
### FR-05 · Error Handling `[MUST]`
 
WebMethods must implement structured error handling at each processing stage.
 
| Error Scenario | Trigger | Handling |
|---|---|---|
| Schema validation failure | Invalid JSON structure | HTTP 400 + log + alert |
| Authentication failure | Invalid token or certificate | HTTP 401 + log |
| Routing rule not matched | Unknown region value | DLQ entry + Operations alert |
| SAP IDoc port unavailable | Connection timeout | Retry 3x with 30s backoff → DLQ |
| SAP IDoc rejected (status 51) | Application error in ZO_SD_LIST | Log WE02 status + alert BA/IT team + DLQ |
| Duplicate composite key | Record already processed | Silent discard + audit log: `DISCARDED` |
| Fan-out partial failure | One SAP instance fails | Retry failed instance only · log partial delivery |
| DLQ entry created | Any unresolvable error | Email alert → Operations team within 60s |
 
---
 
### FR-06 · Dead Letter Queue (DLQ) `[MUST]`
 
All unresolvable messages must be routed to a dedicated Dead Letter Queue.
 
| Requirement | Specification |
|---|---|
| Payload preservation | Full original payload retained |
| Error classification | Error type, code, and timestamp recorded |
| Manual reprocessing | Available via WebMethods IS console |
| Alert on entry | Email to Operations team within 60 seconds |
| DLQ retention | 30 days |
 
---
 
### FR-07 · Audit Logging `[MUST]`
 
Every message processed through WebMethods must generate a structured audit log entry.
 
```json
{
  "wm_message_id":      "WM-2024-07-10-00456",
  "received_at":        "2024-07-10T14:32:01.123Z",
  "source_system":      "vendor-api-engine",
  "correlation_id":     "MCN001_TXN-2024-00123",
  "routing_decision":   "SAP_EMEA",
  "sap_idoc_id":        "IDOC-2024-07-10-00456",
  "we02_status":        "53",
  "we02_status_text":   "Application document posted",
  "uan_reference":      "UAN-2024-DE-004521",
  "processing_status":  "DELIVERED",
  "error_code":         null,
  "retry_count":        0,
  "duration_ms":        1243
}
```
 
Note the inclusion of `we02_status` and `uan_reference` — these allow end-to-end traceability from the vendor API call to the SAP UAN creation confirmation.
 
---
 
### FR-08 · WE02 Status Feedback `[SHOULD]`
 
WebMethods should receive IDoc processing status callbacks from SAP WE02 and update the audit log accordingly.
 
| WE02 Status Code | Meaning | Audit Log Update |
|---|---|---|
| 53 | Application document posted — UAN created | `processing_status: DELIVERED` |
| 51 | Application error — ZO_SD_LIST rejected | `processing_status: SAP_ERROR` + alert |
| 64 | IDoc ready to be transferred | `processing_status: PENDING` |
| 26 | Error during transfer | `processing_status: TRANSFER_ERROR` + retry |
 
---
 
## TRS-6 · Non-Functional Requirements
 
### NFR-01 · Performance
 
| Metric | Requirement |
|---|---|
| End-to-end latency (receipt → SAP delivery) | < 30 seconds under normal load |
| Peak throughput | Minimum 1,000 messages/hour |
| Queue processing latency | < 5 seconds from queue entry to routing |
 
### NFR-02 · Availability
 
| Metric | Requirement |
|---|---|
| WebMethods IS uptime | 99.5% (excluding maintenance windows) |
| Planned maintenance | Sundays 02:00–04:00 UTC |
| Queue persistence across restart | Required |
 
### NFR-03 · Security
 
| Control | Requirement |
|---|---|
| Transport encryption | HTTPS / TLS 1.2+ mandatory |
| Authentication | Required on all inbound service calls |
| Audit log retention | Minimum 12 months (financial compliance) |
| PII handling | No sensitive data retained beyond TTL |
 
### NFR-04 · Scalability
 
| Requirement | Priority |
|---|---|
| New SAP routing targets without core changes | `[MUST]` |
| Routing rules configurable without code deployment | `[MUST]` |
| Horizontal queue capacity scaling | `[SHOULD]` |
 
---
 
## TRS-7 · Data Flow Specification
 
### TRS-7.1 · Inbound Payload — FastAPI → WebMethods
 
```json
{
  "wm_envelope": {
    "source_system":   "vendor-api-engine",
    "message_version": "1.0",
    "sent_at":         "2024-07-10T14:32:00.000Z",
    "correlation_id":  "MCN001_TXN-2024-00123"
  },
  "business_payload": {
    "mcn":                 "MCN001",
    "transactionNumber":   "TXN-2024-00123",
    "customerName":        "Müller GmbH",
    "customerId":          "CUST-DE-4521",
    "resellerPartner":     "PARTNER-EU-789",
    "orderablePartNumber": "PROD-LAP-001",
    "remainingQuantity":   50,
    "entitledPrice":       899.99,
    "currency":            "EUR",
    "region":              "DACH",
    "fulfilmentType":      "Dual",
    "productBrand":        "Hardware",
    "initial":             true,
    "idoc_id":             "IDOC-2024-07-10-00456"
  }
}
```
 
### TRS-7.2 · Field Mapping — JSON → SAP IDoc (ORDERS05)
 
| Source Field (JSON) | IDoc Segment | IDoc Field | Transformation Rule |
|---|---|---|---|
| `mcn` | E1EDK01 | BELNR | Direct copy |
| `transactionNumber` | E1EDK01 | IHREZ | Direct copy |
| `customerName` | E1EDKA1 | NAME1 | Latin-1 encode |
| `customerId` | E1EDKA1 | PARTN | Direct copy |
| `resellerPartner` | E1EDKA1 | PARTN `(role RE)` | Direct copy |
| `orderablePartNumber` | E1EDP01 | MATNR | Direct copy |
| `remainingQuantity` | E1EDP01 | MENGE | Cast → decimal(13,3) |
| `entitledPrice` | E1EDP01 | PREIS | Cast → decimal(11,2) |
| `currency` | E1EDK01 | CURCY | ISO 4217 lookup |
| `region` | E1EDK01 | REGIO | Region YAML table lookup |
| `fulfilmentType` | E1EDK01 | BSART | Fulfilment type YAML mapping |
| `initial` | Control Record | DIRECT | `true` → `1` · `false` → `0` |
 
### TRS-7.3 · Trigger & Event Definitions
 
| Trigger Condition | Event Name | Action |
|---|---|---|
| Inbound POST received | `MESSAGE_RECEIVED` | Create durable queue entry |
| Routing rule matched | `ROUTING_RESOLVED` | Forward to SAP IDoc adapter |
| IDoc delivered to SAP | `IDOC_DELIVERED` | Await WE02 status callback |
| WE02 status 53 received | `UAN_CREATED` | Audit log: `DELIVERED` + UAN reference |
| WE02 status 51 received | `SAP_APPLICATION_ERROR` | DLQ entry + BA/IT alert |
| SAP connection timeout | `ERP_TIMEOUT` | Retry 3x with 30s backoff |
| Retry limit exceeded | `MAX_RETRY_EXCEEDED` | DLQ entry + escalation alert |
| DLQ entry created | `DLQ_ENTRY` | Email alert → Operations team |
| Duplicate key detected | `DUPLICATE_DISCARDED` | Audit log: `DISCARDED` (silent) |
 
---
 
## TRS-8 · Acceptance Criteria
 
| ID | Acceptance Criterion | Test Method | Priority |
|---|---|---|---|
| AC-01 | All inbound messages queued within 2 seconds | Load test: 100 msg/min | `[MUST]` |
| AC-02 | DACH region payload routes to SAP EMEA instance | Integration test with test payload | `[MUST]` |
| AC-03 | `fulfilmentType=Dual` delivers to both SAP instances | Verify both IDoc ports receive IDoc | `[MUST]` |
| AC-04 | SAP timeout triggers 3x retry before DLQ | Simulate SAP downtime, verify retry log | `[MUST]` |
| AC-05 | DLQ entry triggers Operations email within 60 seconds | Manual DLQ injection test | `[MUST]` |
| AC-06 | Duplicate composite key discarded — zero IDoc delivery | Submit identical payload twice | `[MUST]` |
| AC-07 | WE02 status 53 updates audit log with UAN reference | End-to-end test with SAP sandbox | `[MUST]` |
| AC-08 | WE02 status 51 triggers BA/IT alert | Simulate ZO_SD_LIST rejection | `[MUST]` |
| AC-09 | Routing rules updated without redeployment | Update YAML config, verify routing — no restart | `[MUST]` |
| AC-10 | Latin-1 names preserved — Ä, Ö, Ü, ñ intact in IDoc | Test payload with special characters | `[MUST]` |
| AC-11 | 1,000 messages processed within 1 hour | Load test with synthetic data | `[MUST]` |
| AC-12 | DLQ messages manually reprocessable via IS console | Manual reprocess test | `[SHOULD]` |
 
---
 
## TRS-9 · Open Items & Decisions Required
 
| ID | Open Item | Owner | Status |
|---|---|---|---|
| OI-01 | Confirm WebMethods IS version in target environment | IT Infrastructure | Open |
| OI-02 | Confirm SAP IDoc port configuration for EMEA instance | SAP Basis Team | Open |
| OI-03 | Agree authentication method: OAuth 2.0 vs mTLS | Security Team | Open |
| OI-04 | Confirm DLQ alert distribution list — Operations contacts | Business Owner | Open |
| OI-05 | Confirm APAC SAP instance IDoc port availability | SAP Basis Team | Open |
| OI-06 | Define audit log retention policy (financial compliance) | Compliance / Legal | Open |
| OI-07 | Confirm WE02 status callback mechanism — push vs poll | SAP Basis + IT Architecture | Open |
| OI-08 | Define ZO_SD_LIST error code taxonomy for WE02 mapping | SAP SD Functional Team | Open |
 
---
 
## TRS-10 · Glossary
 
| Term | Definition |
|---|---|
| **Ship & Debit** | Vendor pricing program where distributor ships at standard price and claims the discount back from the vendor using an approved UAN |
| **UAN** | Unique Approval Number — SAP reference created by ZO_SD_LIST authorising a Ship & Debit claim |
| **ZO_SD_LIST** | Custom SAP SD transaction for backend Ship & Debit price list creation and UAN generation |
| **WE02** | SAP transaction for IDoc monitoring — displays IDoc status, segments, and processing history |
| **IDoc** | Intermediate Document — SAP's standard format for asynchronous data exchange |
| **iPaaS** | Integration Platform as a Service — middleware platform for connecting enterprise systems |
| **WebMethods IS** | Software AG WebMethods Integration Server — enterprise iPaaS platform |
| **DLQ** | Dead Letter Queue — holding queue for messages that cannot be processed |
| **Fan-out** | Delivering one message to multiple target SAP instances simultaneously |
| **OPGAN** | Cross-system business reference: `MCN_TransactionNumber` |
| **Composite Key** | Unique record identifier derived from MCN, transaction number, part number, quantity, customer ID, and price |
| **ORDERS05** | SAP standard IDoc message type for sales order creation |
| **mTLS** | Mutual TLS — two-way certificate-based authentication |
| **TTL** | Time to Live — maximum time a message persists in the queue before expiry |
 
---
 
## Author
 
**Max Ramos** — Technical Business Analyst & Automation Engineer
 
Enterprise systems integration specialist with 10+ years across SAP ECC environments, REST API integrations, WebMethods middleware coordination, Ship & Debit operations, and process automation across EMEA.
 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-max--ramos-blue)](https://www.linkedin.com/in/max-ramos-6a1942126)
[![GitHub](https://img.shields.io/badge/GitHub-Mcramos0527-black)](https://github.com/Mcramos0527)
[![Portfolio](https://img.shields.io/badge/Portfolio-mcramos0527.github.io-orange)](https://mcramos0527.github.io/maxramos)
 
---
 
## License
 
MIT License — see [LICENSE](LICENSE) for details.
