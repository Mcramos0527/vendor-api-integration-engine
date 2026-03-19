#!/usr/bin/env python3
"""
Seed script to verify configuration files are valid and loadable.
Run this after modifying any YAML configuration.

Usage:
    python scripts/seed_config.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.loader import ConfigLoader


def main():
    loader = ConfigLoader()

    print("=" * 60)
    print("Configuration Validation Report")
    print("=" * 60)

    # Validate regions
    regions = loader.get_valid_regions()
    print(f"\n✓ Regions loaded: {len(regions)}")
    for region in sorted(regions):
        mapping = loader.get_region_mapping(region)
        print(f"  - {region}: entity={mapping.get('entity_code')}, "
              f"countries={mapping.get('countries')}")

    # Validate currencies
    currencies = loader.get_valid_currencies()
    print(f"\n✓ Currencies loaded: {len(currencies)}")
    print(f"  {', '.join(sorted(currencies))}")

    # Validate transaction types
    for ft in ["DUAL", "DIRECT"]:
        tt = loader.get_transaction_type(ft)
        print(f"\n✓ Transaction type '{ft}': erp_type={tt.get('erp_type')}")

    # Validate quantity rules
    qr = loader.get_quantity_rules()
    print(f"\n✓ Quantity rules: max={qr.get('max_single_order')}, "
          f"bulk_threshold={qr.get('bulk_threshold')}")

    print("\n" + "=" * 60)
    print("All configurations valid!")
    print("=" * 60)


if __name__ == "__main__":
    main()
