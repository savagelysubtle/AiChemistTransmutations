"""Display developer license information."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transmutation_codex.core.licensing.supabase_backend import SupabaseBackend

try:
    backend = SupabaseBackend()
    result = (
        backend.client.table("licenses")
        .select("*")
        .eq("email", "dev@aichemist.local")
        .execute()
    )

    if result.data:
        license_data = result.data[0]

        print("=" * 80)
        print("DEVELOPER LICENSE INFORMATION")
        print("=" * 80)
        print(f"\nEmail:           {license_data['email']}")
        print(f"Type:            {license_data['type'].upper()}")
        print(f"Status:          {license_data['status'].upper()}")
        print(f"Max Activations: {license_data['max_activations']}")
        print(f"Created:         {license_data['created_at']}")
        print(f"Expires:         {license_data['expires_at'] or 'Never (Perpetual)'}")
        print(f"\n{'=' * 80}")
        print("LICENSE KEY:")
        print("=" * 80)
        print(license_data["license_key"])
        print("=" * 80)

        print("\n📋 To use this license:")
        print("   1. Copy the license key above")
        print("   2. Use it in your application's license activation")
        print("   3. Or save to: ~/.aichemist/license.json")

    else:
        print("❌ No developer license found in database")
        print("Run: python scripts/generate_dev_license.py")

except Exception as e:
    print(f"❌ Error retrieving license: {e}")
    sys.exit(1)
