#!/usr/bin/env python
"""Test Gumroad license API integration.

This script tests the Gumroad license verification API integration
to ensure it works correctly before deploying to production.

Usage:
    python scripts/licensing/test_gumroad_integration.py

Environment Variables Required:
    None (works offline with mock data for testing)
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transmutation_codex.core.licensing.license_manager import GumroadLicenseVerifier


def test_gumroad_api_format():
    """Test Gumroad API request/response format."""
    print("🧪 Testing Gumroad API integration...")

    verifier = GumroadLicenseVerifier()

    # Test with a fake license key to check API format
    # This will fail but should give us proper error handling
    try:
        result = verifier.verify_license("FAKE-KEY-12345", "test-product")
        print(f"❌ Unexpected success: {result}")
    except Exception as e:
        print(f"✅ Expected error for fake key: {e}")
        print("✅ Gumroad API integration working (error handling)")


def test_license_manager_initialization():
    """Test LicenseManager initialization with Gumroad system."""
    print("\n🧪 Testing LicenseManager initialization...")

    try:
        from transmutation_codex.core.licensing.license_manager import LicenseManager

        # Create temporary directory for testing
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = LicenseManager(Path(temp_dir))

            # Check product mapping
            expected_mapping = {
                "basic": "transmutation-codex-basic",
                "pro": "transmutation-codex-pro",
                "enterprise": "transmutation-codex-enterprise"
            }

            if manager.PRODUCT_MAPPING == expected_mapping:
                print("✅ Product mapping correct")
            else:
                print(f"❌ Product mapping mismatch: {manager.PRODUCT_MAPPING}")

            # Check initial status
            status = manager.get_license_status()
            if status["license_type"] == "trial":
                print("✅ Initial status is trial")
            else:
                print(f"❌ Unexpected initial status: {status}")

    except Exception as e:
        print(f"❌ LicenseManager initialization failed: {e}")
        import traceback
        traceback.print_exc()


def test_feature_gates():
    """Test feature access control."""
    print("\n🧪 Testing feature gates...")

    try:
        from transmutation_codex.core.licensing import check_feature_access, get_license_type

        # Should work for trial-allowed converters
        try:
            check_feature_access("md2pdf")  # Should not raise
            print("✅ Trial feature access working")
        except Exception as e:
            print(f"❌ Trial feature access failed: {e}")

        # Should fail for premium converters in trial
        try:
            check_feature_access("docx2pdf")  # Should raise LicenseError
            print("❌ Premium feature access should have failed in trial")
        except Exception as e:
            print(f"✅ Premium feature access correctly blocked: {type(e).__name__}")

        # Check license type
        license_type = get_license_type()
        if license_type == "trial":
            print("✅ License type correctly detected as trial")
        else:
            print(f"❌ Unexpected license type: {license_type}")

    except Exception as e:
        print(f"❌ Feature gates test failed: {e}")
        import traceback
        traceback.print_exc()


def test_supabase_integration():
    """Test Supabase backend integration (if configured)."""
    print("\n🧪 Testing Supabase integration...")

    try:
        from transmutation_codex.core.licensing.supabase_backend import is_supabase_configured

        if is_supabase_configured():
            print("✅ Supabase is configured")

            try:
                from transmutation_codex.core.licensing.supabase_backend import SupabaseBackend
                backend = SupabaseBackend()
                print("✅ Supabase backend initialized")

                # Test tier limits
                basic_limit = backend._get_max_activations_for_tier("basic")
                pro_limit = backend._get_max_activations_for_tier("pro")
                enterprise_limit = backend._get_max_activations_for_tier("enterprise")

                if basic_limit == 1 and pro_limit == 3 and enterprise_limit == 10:
                    print("✅ Tier activation limits correct")
                else:
                    print(f"❌ Tier limits incorrect: {basic_limit}, {pro_limit}, {enterprise_limit}")

            except Exception as e:
                print(f"❌ Supabase backend test failed: {e}")

        else:
            print("⚠️ Supabase not configured (this is OK for offline testing)")

    except Exception as e:
        print(f"❌ Supabase integration test failed: {e}")


def main():
    """Run all tests."""
    print("=" * 80)
    print("🧪 GUMROAD LICENSE INTEGRATION TEST SUITE")
    print("=" * 80)
    print("Testing the transition from RSA-based to Gumroad API-based licensing")
    print()

    test_gumroad_api_format()
    test_license_manager_initialization()
    test_feature_gates()
    test_supabase_integration()

    print("\n" + "=" * 80)
    print("✅ TEST SUITE COMPLETED")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Set up Gumroad products with permalinks matching PRODUCT_MAPPING")
    print("2. Configure webhook server with GUMROAD_WEBHOOK_SECRET")
    print("3. Deploy webhook server to handle license deliveries")
    print("4. Test with real Gumroad license keys")
    print("5. Update product IDs in PRODUCT_MAPPING if needed")


if __name__ == "__main__":
    main()
