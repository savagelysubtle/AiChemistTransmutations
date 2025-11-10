"""Generate batches of license keys for Gumroad distribution.

This script creates CSV files with license keys that can be uploaded to Gumroad.
Each key is RSA-signed and ready for customer distribution.

Usage:
    # Generate 1000 Basic tier keys
    python scripts/licensing/generate_gumroad_keys.py --count 1000 --tier basic

    # Generate Pro tier keys with custom output
    python scripts/licensing/generate_gumroad_keys.py --count 500 --tier pro --output keys_pro.csv

Requirements:
    - Private key must exist at scripts/licensing/keys/private_key.pem
    - Run generate_rsa_keys.py first if keys don't exist
"""

from __future__ import annotations

import argparse
import csv
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypedDict

    class LicenseKeyData(TypedDict):
        """Type definition for license key data."""

        license_key: str
        tier: str
        max_activations: int
        generated_at: str
        key_id: str

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transmutation_codex.core.licensing.crypto import LicenseCrypto


# License tier configurations
TIER_CONFIG = {
    "basic": {"price": 29, "max_activations": 2, "features": ["Basic conversions"]},
    "pro": {
        "price": 79,
        "max_activations": 5,
        "features": ["Advanced conversions", "Batch processing", "OCR"],
    },
    "enterprise": {
        "price": 299,
        "max_activations": 25,
        "features": [
            "All Pro features",
            "Priority support",
            "Custom integrations",
        ],
    },
}


def load_private_key() -> bytes:
    """Load private key from secure location.

    Returns:
        Private key bytes.

    Raises:
        SystemExit: If private key file not found.
    """
    private_key_path = Path(__file__).parent / "keys" / "private_key.pem"

    if not private_key_path.exists():
        print("❌ Error: Private key not found!")
        print()
        print(f"Expected location: {private_key_path}")
        print()
        print("Please run: python scripts/licensing/generate_rsa_keys.py")
        sys.exit(1)

    with open(private_key_path, "rb") as f:
        return f.read()


def generate_license_key(
    tier: str, max_activations: int, private_key: bytes
) -> tuple[str, str]:
    """Generate a single signed license key.

    Args:
        tier: License tier (basic, pro, enterprise).
        max_activations: Number of allowed device activations.
        private_key: RSA private key bytes.

    Returns:
        Tuple of (license_key, key_id) where key_id is a unique identifier.
    """
    # Generate unique key ID
    key_id = secrets.token_hex(8).upper()

    # Create license data
    license_data = {
        "key_id": key_id,
        "tier": tier,
        "max_activations": max_activations,
        "issued_at": datetime.now().isoformat(),
        "version": "1.0",
    }

    # Generate signed license key
    crypto = LicenseCrypto()
    license_key = crypto.generate_license_key(license_data, private_key)

    return license_key, key_id


def generate_batch(
    count: int, tier: str, output_path: Path, private_key: bytes
) -> list[LicenseKeyData]:
    """Generate a batch of license keys.

    Args:
        count: Number of keys to generate.
        tier: License tier (basic, pro, enterprise).
        output_path: Path to save CSV file.
        private_key: RSA private key bytes.

    Returns:
        List of generated license key data dictionaries.
    """
    tier_config = TIER_CONFIG[tier]
    max_activations = tier_config["max_activations"]

    print(f"Generating {count} {tier.upper()} license keys...")
    print(f"Max activations per key: {max_activations}")
    print()

    licenses: list[LicenseKeyData] = []

    for i in range(1, count + 1):
        license_key, key_id = generate_license_key(tier, max_activations, private_key)

        licenses.append(
            {
                "license_key": license_key,
                "tier": tier,
                "max_activations": max_activations,
                "generated_at": datetime.now().isoformat(),
                "key_id": key_id,
            }
        )

        if i % 100 == 0:
            print(f"  Progress: {i}/{count} keys generated")

    print(f"  Progress: {count}/{count} keys generated")
    print()

    # Save to CSV (Gumroad format)
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Gumroad expects one column: license_key
        writer.writerow(["license_key"])
        for lic in licenses:
            writer.writerow([lic["license_key"]])

    # Also save detailed JSON for our records
    json_path = output_path.with_suffix(".json")
    import json

    with open(json_path, "w", encoding="utf-8") as jsonfile:
        json.dump(licenses, jsonfile, indent=2)

    return licenses


def main() -> None:
    """CLI interface for Gumroad license key generation."""
    parser = argparse.ArgumentParser(
        description="Generate license keys for Gumroad distribution"
    )
    parser.add_argument(
        "--count", type=int, required=True, help="Number of keys to generate"
    )
    parser.add_argument(
        "--tier",
        choices=["basic", "pro", "enterprise"],
        required=True,
        help="License tier",
    )
    parser.add_argument(
        "--output",
        help="Output CSV file (default: keys_{tier}_{timestamp}.csv)",
    )

    args = parser.parse_args()

    # Load private key
    private_key = load_private_key()

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"keys_{args.tier}_{timestamp}.csv")

    # Generate batch
    licenses = generate_batch(args.count, args.tier, output_path, private_key)

    # Print summary
    print("✅ License keys generated successfully!")
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Tier: {args.tier.upper()}")
    print(f"Keys Generated: {len(licenses)}")
    print(f"Max Activations: {TIER_CONFIG[args.tier]['max_activations']}")
    print()
    print("Output Files:")
    print(f"  CSV (for Gumroad): {output_path.resolve()}")
    print(f"  JSON (for records): {output_path.with_suffix('.json').resolve()}")
    print()
    print("Sample Key:")
    print("-" * 70)
    print(licenses[0]["license_key"])
    print("-" * 70)
    print()
    print("Next Steps:")
    print("1. Upload CSV to Gumroad product settings")
    print("2. Insert keys into Supabase database:")
    print(
        f"   python scripts/licensing/insert_license_keys.py --csv {output_path} --tier {args.tier}"
    )
    print("3. Test purchase flow")
    print()


if __name__ == "__main__":
    main()





