"""Quick script to verify Supabase license integration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transmutation_codex.core.licensing.supabase_backend import SupabaseBackend

# Test connection
backend = SupabaseBackend()
print("🔍 Testing Supabase Integration")
print("=" * 50)
print(f"✅ Connected to: {backend.client.supabase_url}")
print(f"✅ Online status: {backend.is_online_available()}")

# Check for dev license
print("\n📋 Checking for dev license...")
result = (
    backend.client.table("licenses")
    .select("*")
    .eq("email", "dev@aichemist.local")
    .execute()
)

if result.data:
    license_data = result.data[0]
    print("✅ License found in Supabase!")
    print(f"  ID: {license_data['id']}")
    print(f"  Email: {license_data['email']}")
    print(f"  Type: {license_data['type']}")
    print(f"  Status: {license_data['status']}")
    print(f"  Max Activations: {license_data['max_activations']}")
    print(f"  Created: {license_data['created_at']}")
    print(f"  License Key: {license_data['license_key'][:50]}...")

    # Test validation
    print("\n🧪 Testing license validation...")
    is_valid, license_info, message = backend.validate_license_online(
        license_data["license_key"]
    )
    if is_valid:
        print("✅ License validation: SUCCESS")
        print(f"   License Type: {license_info.get('license_type')}")
        print(f"   Max Activations: {license_info.get('max_activations')}")
    else:
        print("❌ License validation: FAILED")
        print(f"   Message: {message}")
else:
    print("❌ No license found for dev@aichemist.local")
    print("   Please insert the license using SQL in Supabase Dashboard")

print("\n" + "=" * 50)
print("✅ Supabase integration test complete!")
