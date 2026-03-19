# Configuration Guide

## Overview

Business rules are externalized as YAML configuration files in the `config/` directory. This allows rules to change without code deployments — just update the YAML file and restart the service.

## Configuration Files

### transaction_types.yaml

Maps fulfilment types to ERP document types.

```yaml
types:
  DUAL:
    erp_type: "ZKE"
    description: "Dual fulfillment"
    requires_warehouse: true
```

**When to modify:** When a new fulfilment type is introduced or an ERP document type mapping changes.

### currency_logic.yaml

Defines default and allowed currencies per business region.

```yaml
regions:
  DACH:
    default_currency: "EUR"
    allowed_currencies: ["EUR"]
    decimal_places: 2
```

**When to modify:** When a new region is onboarded, a currency is added or removed, or regional currency rules change.

### region_mapping.yaml

Maps business regions to entity codes and country lists.

```yaml
regions:
  DACH:
    entity_code: "1000"
    countries: ["DE", "AT", "CH"]
    timezone: "Europe/Berlin"
```

**When to modify:** When a new region is onboarded, an entity code changes, or countries are reassigned between regions.

### quantity_rules.yaml

Defines quantity validation thresholds.

```yaml
max_single_order: 99999
min_quantity: 1
bulk_threshold: 1000
```

**When to modify:** When quantity limits change based on business decisions.

## Environment Variables

Application behavior is controlled via environment variables (`.env` file in development):

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Runtime environment |
| `DEBUG` | `true` | Enable debug mode |
| `PORT` | `8000` | API port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `CTO_FLAG_ENABLED` | `false` | Enable Configure-to-Order processing |
| `BATCH_PROCESSING_ENABLED` | `false` | Enable batch endpoint |
| `DATABASE_URL` | `sqlite:///./data/vendor_api.db` | Database connection |

## Adding a New Region

1. Add the region entry to `region_mapping.yaml` with entity code and countries
2. Add currency rules for the region in `currency_logic.yaml`
3. Restart the service
4. No code changes needed
