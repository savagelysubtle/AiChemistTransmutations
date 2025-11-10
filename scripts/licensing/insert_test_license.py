#!/usr/bin/env python
"""Insert the existing test license key into Supabase.

This script takes the already-generated DEV_LICENSE.txt key and inserts it
into Supabase so the app can verify it during activation.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from supabase import create_client
except ImportError:
    print("ERROR: supabase-py is not installed.")
    print("Install with: uv add supabase")
    sys.exit(1)


def main():
    """Insert test license into Supabase."""
    # Read the license key from DEV_LICENSE.txt
    license_file = Path(__file__).parent.parent.parent / "DEV_LICENSE.txt"

    if not license_file.exists():
        print(f"ERROR: {license_file} not found!")
        print(
            "Generate it first with: python scripts/licensing/generate_dev_license.py --print-only"
        )
        sys.exit(1)

    # Extract license key from file
    with open(license_file) as f:
        content = f.read()

    # Find the license key (starts with AICHEMIST:)
    license_key = None
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("AICHEMIST:"):
            license_key = line
            break

    if not license_key:
        print("ERROR: Could not find license key in DEV_LICENSE.txt")
        sys.exit(1)

    print("=" * 80)
    print("INSERTING TEST LICENSE INTO SUPABASE")
    print("=" * 80)
    print(f"\nLicense Key: {license_key[:50]}...")
    print()

    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("ERROR: Supabase credentials not found!")
        print()
        print("Set environment variables:")
        print("  SUPABASE_URL=your-project-url")
        print("  SUPABASE_SERVICE_KEY=your-service-role-key")
        print()
        print("OR manually insert into Supabase SQL editor:")
        print()
        print(
            "  INSERT INTO licenses (email, license_key, type, status, max_activations, metadata)"
        )
        print(
            f"  VALUES ('dev@aichemist.local', '{license_key}', 'enterprise', 'active', 999, '{{}}'::jsonb);"
        )
        print()
        sys.exit(1)

    # Create Supabase client
    client = create_client(url, key)

    try:
        # Check if license already exists
        print("Checking for existing license...")
        existing = (
            client.table("licenses")
            .select("*")
            .eq("email", "dev@aichemist.local")
            .execute()
        )

        if existing.data:
            print(f"\n⚠️  Dev license already exists (ID: {existing.data[0]['id']})")
            print("\nOptions:")
            print("  1. Delete old license and insert new one")
            print("  2. Keep existing license")
            print("  3. Cancel")
            print()
            choice = input("Enter choice (1/2/3): ").strip()

            if choice == "1":
                print(f"Deleting license ID {existing.data[0]['id']}...")
                client.table("licenses").delete().eq(
                    "id", existing.data[0]["id"]
                ).execute()
                print("✓ Deleted existing license")
            elif choice == "2":
                print("\nKeeping existing license. Use this key in the app:")
                print(existing.data[0]["license_key"])
                return
            else:
                print("Cancelled.")
                return

        # Insert new license
        print("\nInserting license into Supabase...")
        record = {
            "email": "dev@aichemist.local",
            "license_key": license_key,
            "type": "enterprise",
            "status": "active",
            "max_activations": 999,
            "expires_at": None,  # Perpetual
            "metadata": {
                "is_dev_license": True,
                "description": "Test license for development",
                "created_by": "insert_test_license.py",
                "created_at": datetime.now().isoformat(),
            },
        }

        result = client.table("licenses").insert(record).execute()

        if result.data:
            print("\n" + "=" * 80)
            print("✅ SUCCESS! License inserted into Supabase")
            print("=" * 80)
            print()
            print("Database Record:")
            print(f"  ID: {result.data[0]['id']}")
            print(f"  Email: {result.data[0]['email']}")
            print(f"  Type: {result.data[0]['type']}")
            print(f"  Status: {result.data[0]['status']}")
            print(f"  Max Activations: {result.data[0]['max_activations']}")
            print()
            print("=" * 80)
            print("NOW TEST IN YOUR APP:")
            print("=" * 80)
            print()
            print("1. Run your installed app")
            print("2. Click 'Activate License'")
            print("3. Paste this key:")
            print()
            print(f"   {license_key}")
            print()
            print("4. Click 'Activate'")
            print("5. Should show 'Licensed' or 'Pro' status")
            print()
            print("=" * 80)
        else:
            print("\nERROR: Failed to insert license")
            sys.exit(1)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
