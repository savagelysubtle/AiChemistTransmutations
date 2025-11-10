"""Insert generated license keys into Supabase database.

This script reads license keys from CSV or JSON and inserts them into Supabase
with status 'pending' (not activated). Keys become 'active' when customers
first use them.

Usage:
    python scripts/licensing/insert_license_keys.py --csv keys_basic.csv --tier basic
    python scripts/licensing/insert_license_keys.py --json keys_pro.json --tier pro

Environment Variables:
    SUPABASE_URL: Your Supabase project URL
    SUPABASE_SERVICE_KEY: Service role key (has admin access)

Requirements:
    - Supabase project with licenses table created
    - Environment variables configured
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase-py not installed!")
    print()
    print("Install with: pip install supabase")
    sys.exit(1)


# License tier configurations
TIER_CONFIG = {
    "basic": {"max_activations": 2, "features": ["Basic conversions"], "db_type": "basic"},
    "pro": {
        "max_activations": 5,
        "features": ["Advanced conversions", "Batch processing", "OCR"],
        "db_type": "professional",  # Database uses 'professional', not 'pro'
    },
    "enterprise": {
        "max_activations": 25,
        "features": [
            "All Pro features",
            "Priority support",
            "Custom integrations",
        ],
        "db_type": "enterprise",
    },
}


def get_supabase_client() -> Client:
    """Create Supabase client from environment variables.

    Returns:
        Authenticated Supabase client.

    Raises:
        SystemExit: If environment variables not set.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Error: Supabase credentials not found!")
        print()
        print("Set environment variables:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_SERVICE_KEY=your-service-role-key")
        print()
        sys.exit(1)

    return create_client(url, key)


def read_keys_from_csv(csv_path: Path) -> list[dict[str, Any]]:
    """Read license keys from CSV file.

    Args:
        csv_path: Path to CSV file with license_key column.

    Returns:
        List of dictionaries containing license key data.
    """
    keys = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "license_key" in row:
                keys.append({"license_key": row["license_key"]})

    return keys


def read_keys_from_json(json_path: Path) -> list[dict[str, Any]]:
    """Read license keys from JSON file.

    Args:
        json_path: Path to JSON file with license key data.

    Returns:
        List of dictionaries containing license key data.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def insert_keys_to_supabase(
    client: Client, keys: list[dict[str, Any]], tier: str
) -> tuple[int, int]:
    """Insert license keys into Supabase database.

    Args:
        client: Authenticated Supabase client.
        keys: List of license key dictionaries.
        tier: License tier (basic, pro, enterprise).

    Returns:
        Tuple of (successful_inserts, failed_inserts).
    """
    tier_config = TIER_CONFIG[tier]
    successful = 0
    failed = 0

    print(f"Inserting {len(keys)} keys into Supabase...")
    print()

    for i, key_data in enumerate(keys, 1):
        license_key = key_data["license_key"]

        # Prepare database record
        # Note: Database schema uses 'type' instead of 'tier', and doesn't have 'features' or 'generated_at' columns
        record = {
            "license_key": license_key,
            "type": tier_config["db_type"],  # DB column is 'type', using mapped value (pro -> professional)
            "email": "",  # Required column, empty for pre-generated keys
            "status": "active",  # Pre-generated keys are active, will be marked 'used' on first activation
            "max_activations": tier_config["max_activations"],
            "activations_count": 0,
            # Note: 'features' stored in metadata JSON instead
            "metadata": {
                "key_id": key_data.get("key_id"),
                "source": "gumroad_batch",
                "features": tier_config["features"],
            },
        }

        try:
            # Insert into licenses table
            client.table("licenses").insert(record).execute()
            successful += 1

            if i % 100 == 0:
                print(f"  Progress: {i}/{len(keys)} keys inserted")

        except Exception as e:
            failed += 1
            print(f"  ⚠️  Failed to insert key {i}: {e}")

    print(f"  Progress: {len(keys)}/{len(keys)} keys processed")
    print()

    return successful, failed


def main() -> None:
    """CLI interface for inserting license keys into Supabase."""
    parser = argparse.ArgumentParser(
        description="Insert license keys into Supabase database"
    )

    # Input source (CSV or JSON)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--csv", type=Path, help="CSV file with license keys")
    input_group.add_argument("--json", type=Path, help="JSON file with license keys")

    parser.add_argument(
        "--tier",
        choices=["basic", "pro", "enterprise"],
        required=True,
        help="License tier",
    )

    args = parser.parse_args()

    # Read keys from file
    if args.csv:
        if not args.csv.exists():
            print(f"❌ Error: CSV file not found: {args.csv}")
            sys.exit(1)
        keys = read_keys_from_csv(args.csv)
        source_file = args.csv
    else:
        if not args.json.exists():
            print(f"❌ Error: JSON file not found: {args.json}")
            sys.exit(1)
        keys = read_keys_from_json(args.json)
        source_file = args.json

    if not keys:
        print(f"❌ Error: No keys found in {source_file}")
        sys.exit(1)

    print(f"Found {len(keys)} keys in {source_file}")
    print()

    # Get Supabase client
    client = get_supabase_client()

    # Insert keys
    successful, failed = insert_keys_to_supabase(client, keys, args.tier)

    # Print summary
    print("=" * 70)
    print("INSERTION COMPLETE")
    print("=" * 70)
    print(f"Source File: {source_file}")
    print(f"Tier: {args.tier.upper()}")
    print(f"Total Keys: {len(keys)}")
    print(f"✅ Successful: {successful}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print()

    if successful > 0:
        print("✅ Keys ready for Gumroad distribution!")
        print()
        print("Next Steps:")
        print(f"1. Upload {source_file} to Gumroad product settings")
        print("2. Configure license key delivery in Gumroad")
        print("3. Test purchase flow")
    else:
        print("❌ No keys were inserted successfully!")
        print("Check Supabase credentials and table schema.")


if __name__ == "__main__":
    main()

