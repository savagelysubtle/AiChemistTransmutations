"""Generate license keys for customers.

This script is used to create signed license keys that can be distributed
to customers via Gumroad, Stripe, or Microsoft Store.

Usage:
    python scripts/generate_license.py --email customer@example.com --type pro
    python scripts/generate_license.py --email test@test.com --type trial --batch 10

Requirements:
    - Private key must be available at scripts/keys/private_key.pem
    - Run generate_rsa_keys.py first if keys don't exist
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transmutation_codex.core.licensing.crypto import LicenseCrypto


def load_private_key() -> bytes:
    """Load private key from secure location."""
    private_key_path = Path(__file__).parent / "keys" / "private_key.pem"

    if not private_key_path.exists():
        print("❌ Error: Private key not found!")
        print()
        print(f"Expected location: {private_key_path}")
        print()
        print("Please run: python scripts/generate_rsa_keys.py")
        sys.exit(1)

    with open(private_key_path, "rb") as f:
        return f.read()


def generate_license(
    email: str,
    license_type: str = "pro",
    max_activations: int = 1,
    expiry_days: int | None = None,
    customer_name: str | None = None,
    order_id: str | None = None,
) -> str:
    """Generate a signed license key.

    Args:
        email: Customer email address
        license_type: License type (trial, pro, enterprise)
        max_activations: Number of allowed device activations
        expiry_days: Days until expiry (None for perpetual)
        customer_name: Optional customer name
        order_id: Optional order/transaction ID

    Returns:
        Signed license key string
    """
    # Load private key
    private_key = load_private_key()

    # Create license data
    license_data = {
        "email": email,
        "type": license_type,
        "max_activations": max_activations,
        "issued_at": datetime.now().isoformat(),
        "version": "1.0",
    }

    # Add optional fields
    if expiry_days:
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        license_data["expires_at"] = expiry_date.isoformat()

    if customer_name:
        license_data["name"] = customer_name

    if order_id:
        license_data["order_id"] = order_id

    # Generate signed license key
    crypto = LicenseCrypto()
    license_key = crypto.generate_license_key(license_data, private_key)

    return license_key


def main():
    """CLI interface for license generation."""
    parser = argparse.ArgumentParser(
        description="Generate license keys for AiChemist Transmutation Codex"
    )
    parser.add_argument(
        "--email", required=True, help="Customer email address"
    )
    parser.add_argument(
        "--type",
        choices=["trial", "pro", "enterprise"],
        default="pro",
        help="License type (default: pro)",
    )
    parser.add_argument(
        "--name", help="Customer name (optional)"
    )
    parser.add_argument(
        "--order-id", help="Order/transaction ID (optional)"
    )
    parser.add_argument(
        "--activations",
        type=int,
        default=1,
        help="Maximum device activations (default: 1)",
    )
    parser.add_argument(
        "--expiry-days",
        type=int,
        help="Days until expiry (omit for perpetual license)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        help="Generate multiple licenses with sequential email suffixes",
    )
    parser.add_argument(
        "--output",
        help="Output file for batch generation (default: licenses.json)",
    )

    args = parser.parse_args()

    # Generate single or batch licenses
    if args.batch:
        generate_batch(args)
    else:
        generate_single(args)


def generate_single(args):
    """Generate a single license key."""
    print("Generating license key...")
    print()

    license_key = generate_license(
        email=args.email,
        license_type=args.type,
        max_activations=args.activations,
        expiry_days=args.expiry_days,
        customer_name=args.name,
        order_id=args.order_id,
    )

    print("✅ License key generated successfully!")
    print()
    print("=" * 70)
    print("LICENSE KEY")
    print("=" * 70)
    print(license_key)
    print("=" * 70)
    print()
    print("License Details:")
    print(f"  Email: {args.email}")
    print(f"  Type: {args.type}")
    print(f"  Max Activations: {args.activations}")
    if args.expiry_days:
        expiry_date = datetime.now() + timedelta(days=args.expiry_days)
        print(f"  Expires: {expiry_date.strftime('%Y-%m-%d')}")
    else:
        print(f"  Expires: Never (perpetual)")
    if args.name:
        print(f"  Name: {args.name}")
    if args.order_id:
        print(f"  Order ID: {args.order_id}")
    print()


def generate_batch(args):
    """Generate multiple license keys."""
    print(f"Generating {args.batch} license keys...")
    print()

    licenses = []
    email_base = args.email.split("@")[0]
    email_domain = args.email.split("@")[1]

    for i in range(1, args.batch + 1):
        email = f"{email_base}+{i}@{email_domain}"
        order_id = f"{args.order_id}-{i:03d}" if args.order_id else None

        license_key = generate_license(
            email=email,
            license_type=args.type,
            max_activations=args.activations,
            expiry_days=args.expiry_days,
            customer_name=args.name,
            order_id=order_id,
        )

        licenses.append(
            {
                "email": email,
                "type": args.type,
                "license_key": license_key,
                "order_id": order_id,
                "generated_at": datetime.now().isoformat(),
            }
        )

        print(f"  [{i}/{args.batch}] Generated for {email}")

    # Save to file
    output_file = args.output or "licenses.json"
    output_path = Path(output_file)

    with open(output_path, "w") as f:
        json.dump(licenses, f, indent=2)

    print()
    print(f"✅ Generated {args.batch} licenses successfully!")
    print(f"📄 Saved to: {output_path.resolve()}")
    print()
    print("Sample license key:")
    print("=" * 70)
    print(licenses[0]["license_key"])
    print("=" * 70)


if __name__ == "__main__":
    main()
