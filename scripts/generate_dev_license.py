"""Generate and insert a lifetime developer license.

This script creates a perpetual enterprise license for the development account
and inserts it into the Supabase database.

The dev license has:
- Email: dev@aichemist.local
- Type: enterprise (all features)
- Max Activations: 999 (unlimited for dev purposes)
- Expires: Never (perpetual)
- Status: active
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from supabase import create_client
except ImportError:
    print("ERROR: supabase-py is not installed.")
    print("Install with: pip install supabase")
    sys.exit(1)

from transmutation_codex.core.licensing.crypto import LicenseCrypto


# Developer license configuration
DEV_LICENSE_CONFIG = {
    "email": "dev@aichemist.local",
    "license_type": "enterprise",
    "max_activations": 999,
    "expires_at": None,  # Perpetual
    "features": ["all"],
    "metadata": {
        "is_dev_license": True,
        "description": "Lifetime developer license",
        "created_by": "generate_dev_license.py",
    },
}


def generate_license_key(private_key_path: str | None = None) -> tuple[str, dict]:
    """Generate a cryptographically signed license key.

    Args:
        private_key_path: Path to private key file (generates new if not provided)

    Returns:
        Tuple of (license_key, license_data)
    """
    crypto = LicenseCrypto()

    # Generate or load private key
    if private_key_path and Path(private_key_path).exists():
        print(f"Loading private key from {private_key_path}")
        with open(private_key_path, "rb") as f:
            private_key_pem = f.read()
    else:
        print("Generating new RSA key pair...")
        private_key_pem, public_key_pem = crypto.generate_key_pair()

        # Save keys
        keys_dir = Path(__file__).parent.parent / ".keys"
        keys_dir.mkdir(exist_ok=True)

        private_path = keys_dir / "private_key.pem"
        public_path = keys_dir / "public_key.pem"

        with open(private_path, "wb") as f:
            f.write(private_key_pem)
        with open(public_path, "wb") as f:
            f.write(public_key_pem)

        print(f"Saved private key to: {private_path}")
        print(f"Saved public key to: {public_path}")
        print("\nWARNING: Keep private key secure! It's used to sign license keys.")

    # Prepare license data
    license_data = {
        "email": DEV_LICENSE_CONFIG["email"],
        "license_type": DEV_LICENSE_CONFIG["license_type"],
        "max_activations": DEV_LICENSE_CONFIG["max_activations"],
        "features": DEV_LICENSE_CONFIG["features"],
        "issued_at": datetime.now().isoformat(),
    }

    # Add expiry if specified
    if DEV_LICENSE_CONFIG["expires_at"]:
        license_data["expiry_date"] = DEV_LICENSE_CONFIG["expires_at"]

    # Generate signed license key
    license_key = crypto.generate_license_key(license_data, private_key_pem)

    return license_key, license_data


def insert_into_supabase(license_key: str, license_data: dict) -> dict:
    """Insert license into Supabase database.

    Args:
        license_key: Generated license key
        license_data: License metadata

    Returns:
        Inserted license record
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        print("\nSet environment variables:")
        print("  export SUPABASE_URL='https://your-project.supabase.co'")
        print("  export SUPABASE_ANON_KEY='your-anon-key'")
        sys.exit(1)

    client = create_client(url, key)

    print("\nInserting license into Supabase...")

    try:
        # Check if dev license already exists
        existing = client.table("licenses").select("*").eq(
            "email", DEV_LICENSE_CONFIG["email"]
        ).execute()

        if existing.data:
            print(f"\nWARNING: Dev license already exists (ID: {existing.data[0]['id']})")
            overwrite = input("Overwrite existing license? (yes/no): ").lower()
            if overwrite != "yes":
                print("Aborted.")
                return existing.data[0]

            # Delete old license (cascades to activations and usage_logs)
            client.table("licenses").delete().eq("id", existing.data[0]["id"]).execute()
            print("Deleted existing dev license.")

        # Insert new license
        record = {
            "email": DEV_LICENSE_CONFIG["email"],
            "license_key": license_key,
            "type": DEV_LICENSE_CONFIG["license_type"],
            "status": "active",
            "max_activations": DEV_LICENSE_CONFIG["max_activations"],
            "expires_at": DEV_LICENSE_CONFIG["expires_at"],
            "metadata": DEV_LICENSE_CONFIG["metadata"],
        }

        result = client.table("licenses").insert(record).execute()

        if result.data:
            print("\n✓ Developer license created successfully!")
            return result.data[0]
        else:
            print("\nERROR: Failed to insert license")
            sys.exit(1)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def save_license_to_file(license_key: str, license_data: dict, db_record: dict):
    """Save license information to a file for reference.

    Args:
        license_key: Generated license key
        license_data: License metadata
        db_record: Database record from Supabase
    """
    output_dir = Path(__file__).parent.parent / ".licenses"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "dev_license.txt"

    content = f"""
================================================================================
AICHEMIST TRANSMUTATION CODEX - DEVELOPER LICENSE
================================================================================

LICENSE KEY:
{license_key}

LICENSE DETAILS:
- Email: {DEV_LICENSE_CONFIG['email']}
- Type: {DEV_LICENSE_CONFIG['license_type']}
- Max Activations: {DEV_LICENSE_CONFIG['max_activations']}
- Expires: {'Never (Perpetual)' if not DEV_LICENSE_CONFIG['expires_at'] else DEV_LICENSE_CONFIG['expires_at']}
- Status: active

DATABASE RECORD:
- ID: {db_record.get('id')}
- Created: {db_record.get('created_at')}

FEATURES:
- All converters unlocked
- Unlimited file sizes
- Unlimited conversions
- Developer/testing features enabled

NOTES:
- This is a development license for internal use only
- Do not share this license key publicly
- Can be activated on up to {DEV_LICENSE_CONFIG['max_activations']} machines

================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================
"""

    with open(output_file, "w") as f:
        f.write(content.strip())

    print(f"\nLicense details saved to: {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate lifetime developer license for AiChemist"
    )
    parser.add_argument(
        "--private-key",
        type=str,
        help="Path to existing private key (generates new if not provided)",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Only generate and print license key (don't insert into DB)",
    )

    args = parser.parse_args()

    print("=" * 80)
    print("AICHEMIST DEVELOPER LICENSE GENERATOR")
    print("=" * 80)

    # Generate license key
    license_key, license_data = generate_license_key(args.private_key)

    print("\n" + "=" * 80)
    print("GENERATED LICENSE KEY:")
    print("=" * 80)
    print(f"\n{license_key}\n")
    print("=" * 80)

    if args.print_only:
        print("\nLicense key generated successfully!")
        print("Use --print-only=false to insert into Supabase database.")
        return

    # Insert into Supabase
    db_record = insert_into_supabase(license_key, license_data)

    # Save to file
    save_license_to_file(license_key, license_data, db_record)

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("\n1. Activate the license in your application:")
    print(f"   python -m transmutation_codex.adapters.cli.main activate {license_key}")
    print("\n2. Or manually add to your license file:")
    print(f"   ~/.aichemist/license.json")
    print("\n3. Verify license status:")
    print("   python -m transmutation_codex.adapters.cli.main license-status")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
