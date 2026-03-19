# Architecture Guide

## System Overview

The Vendor API Integration Engine is a middleware service that sits between external vendor systems and an internal ERP platform. It receives product catalog and special pricing data via REST API, validates and transforms it, and generates ERP-compatible Intermediate Documents (IDocs) for automated processing.

## Design Principles

**Separation of Concerns** — Each stage of the processing pipeline is isolated: validation, transformation, generation, and auditing are independent modules that can be tested, debugged, and modified independently.

**Configuration over Code** — Business rules that change frequently (transaction types, currency mappings, region definitions) are externalized as YAML files. This allows business teams to request changes that don't require code deployments.

**Idempotency** — The composite key deduplication mechanism ensures that reprocessing the same payload does not create duplicate ERP documents. This is critical for reliability in distributed systems.

**Audit-First** — Every processing event is logged with timestamps, severity levels, and request correlation IDs. This enables full traceability for compliance and debugging.

## Processing Pipeline

### 1. API Gateway Layer

FastAPI receives the incoming JSON payload and performs initial schema validation using Pydantic models. Invalid payloads are rejected immediately with structured error responses.

### 2. Business Rule Validation

The validation engine checks the payload against configurable business rules:
- Reseller partner must be present (mandatory for IDoc creation)
- Region must exist in the region mapping configuration
- Currency must be valid for the specified region
- Fulfilment type must be a recognized value
- OPGAN format constraints (MCN cannot contain underscore separator)
- Quantity must fall within configured thresholds

### 3. Composite Key Deduplication

A SHA-256 hash is computed from six fields: mcn, transactionNumber, orderablePartNumber, remainingQuantity, customerId, and entitledPrice. If this composite key already exists in the registry, the request is rejected with a 409 Conflict response.

### 4. Field Transformation

The field mapper transforms vendor field names and values into ERP-compatible formats:
- Generate OPGAN reference (MCN_TransactionNumber format)
- Encode customer names for Latin-1 compatibility
- Resolve region to entity code
- Map fulfilment type to ERP transaction type

### 5. Product Categorization

Products are classified based on the productBrand field:
- "Services" or "Software" → Software / Service
- Everything else → Hardware

This classification drives downstream ERP document type selection and tax handling.

### 6. IDoc Generation

The generator creates a complete IDoc document with header (control record), segment (business data), and audit metadata. Each IDoc receives a unique identifier and is registered in the IDoc store.

## Double Execution Pattern

The ERP system requires a two-phase commit for sales agreements:

1. **Phase 1 (INITIAL=True):** Creates the base document structure in the ERP system
2. **Phase 2 (INITIAL=False):** Finalizes and activates the agreement

Both phases use the same API endpoint. The `initial` flag in the payload determines the processing mode. The engine handles both phases transparently.

## Feature Flag Architecture

The CTO (Configure-to-Order) flag demonstrates the feature flag pattern. It was designed to allow future activation without code changes — when the procurement team completes their process changes, the flag can be enabled via environment variable.

Feature flags are read from environment variables at startup and can be checked anywhere in the pipeline via the `FeatureFlags` utility class.

## Error Handling Strategy

| Error Type | HTTP Status | Response |
|-----------|-------------|----------|
| Invalid schema | 422 | Structured error list |
| Missing reseller partner | 422 | Specific validation error |
| Duplicate composite key | 409 | Reference to existing IDoc |
| IDoc not found | 404 | Not found message |
| Internal error | 500 | Error ID for support |

## Scalability Considerations

The current implementation uses in-memory stores for the composite key registry and IDoc tracking. For production deployment:

- **Composite Key Registry:** Move to PostgreSQL or Redis for persistence and horizontal scaling
- **IDoc Store:** Move to PostgreSQL with proper indexing on idoc_id and opgan
- **Audit Logs:** Stream to a centralized logging platform (ELK, Datadog, etc.)
- **Rate Limiting:** Add Redis-backed rate limiting per API key
