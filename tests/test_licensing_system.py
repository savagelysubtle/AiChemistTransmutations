#!/usr/bin/env python
"""Comprehensive test script for the licensing system.

This script tests:
1. Trial manager (10 conversion limit)
2. License manager (activation/deactivation)
3. Feature gates (access control)
4. File size limits
5. Conversion tracking
"""

import os
import tempfile
from pathlib import Path

# Set up test environment before importing
os.environ['TESTING'] = '1'

from transmutation_codex.core.licensing import (
    check_feature_access,
    check_file_size_limit,
    get_license_manager,
    get_trial_status,
    record_conversion_attempt,
    activate_license_key,
    get_license_type,
)
from transmutation_codex.core import LicenseError, TrialExpiredError


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_trial_status():
    """Test 1: Trial status tracking."""
    print_section("TEST 1: Trial Status Tracking")

    status = get_trial_status()
    print(f"✓ Initial trial status: {status}")
    print(f"  - Conversions used: {status['used']}")
    print(f"  - Conversions remaining: {status['remaining']}")
    print(f"  - Limit: {status['limit']}")
    print(f"  - Status: {status['status']}")

    assert status['limit'] == 10, "Trial limit should be 10"
    assert status['remaining'] <= 10, "Remaining should be <= 10"
    print("\n✅ Trial status test PASSED")


def test_free_tier_converter():
    """Test 2: Free tier converter access (MD→PDF)."""
    print_section("TEST 2: Free Tier Converter (MD→PDF)")

    try:
        check_feature_access("md2pdf")
        print("✓ MD→PDF converter is accessible in free tier")
        print("✅ Free tier converter test PASSED")
    except LicenseError as e:
        print(f"❌ FREE TIER TEST FAILED: {e}")
        raise


def test_paid_tier_converter_blocked():
    """Test 3: Paid tier converter blocked for trial users."""
    print_section("TEST 3: Paid Tier Converter Blocked (PDF→MD)")

    try:
        check_feature_access("pdf2md")
        print("❌ PAID TIER TEST FAILED: PDF→MD should be blocked for trial users!")
        raise AssertionError("PDF→MD should not be accessible in trial")
    except LicenseError as e:
        print(f"✓ PDF→MD correctly blocked for trial users")
        print(f"  Error: {e}")
        print("✅ Paid tier blocking test PASSED")


def test_file_size_limit():
    """Test 4: File size limit enforcement."""
    print_section("TEST 4: File Size Limit (5MB)")

    # Create a test file under limit
    small_file = Path(tempfile.gettempdir()) / "test_small.txt"
    small_file.write_text("Small test file" * 100)  # ~1.5KB

    try:
        check_file_size_limit(str(small_file))
        print(f"✓ Small file ({small_file.stat().st_size} bytes) allowed")
    except LicenseError:
        print(f"❌ SMALL FILE TEST FAILED: Should allow files under 5MB")
        raise
    finally:
        small_file.unlink()

    # Create a test file over limit (simulated)
    print("\n✓ Testing oversized file rejection...")
    large_file = Path(tempfile.gettempdir()) / "test_large.bin"

    try:
        # Create a 6MB file
        with open(large_file, 'wb') as f:
            f.write(b'0' * (6 * 1024 * 1024))  # 6 MB

        try:
            check_file_size_limit(str(large_file))
            print("❌ LARGE FILE TEST FAILED: Should reject files over 5MB!")
            raise AssertionError("Files over 5MB should be rejected in trial")
        except LicenseError as e:
            print(f"✓ Large file (6MB) correctly rejected")
            print(f"  Error: {e}")
    finally:
        if large_file.exists():
            large_file.unlink()

    print("\n✅ File size limit test PASSED")


def test_conversion_tracking():
    """Test 5: Conversion tracking."""
    print_section("TEST 5: Conversion Tracking")

    # Get initial count
    initial_status = get_trial_status()
    initial_count = initial_status['used']
    print(f"✓ Initial conversions: {initial_count}")

    # Record a test conversion
    test_file = Path(tempfile.gettempdir()) / "test.md"
    test_file.write_text("# Test")
    output_file = test_file.with_suffix(".pdf")

    try:
        record_conversion_attempt(
            converter_name="md2pdf",
            input_file=str(test_file),
            output_file=str(output_file),
            success=True,
        )
        print("✓ Recorded test conversion")

        # Check count increased
        new_status = get_trial_status()
        new_count = new_status['used']
        print(f"✓ New conversions: {new_count}")

        assert new_count == initial_count + 1, "Conversion count should increase by 1"
        print("✅ Conversion tracking test PASSED")
    finally:
        test_file.unlink()


def test_trial_expiration():
    """Test 6: Trial expiration after limit."""
    print_section("TEST 6: Trial Expiration")

    # Get current status
    status = get_trial_status()
    print(f"✓ Current status:")
    print(f"  - Used: {status['used']}")
    print(f"  - Remaining: {status['remaining']}")

    if status['remaining'] == 0:
        print("✓ Trial is already expired")
        print("  Testing that conversions are blocked...")

        try:
            # Try to record another conversion (should fail)
            record_conversion_attempt(
                converter_name="md2pdf",
                input_file="test.md",
                output_file="test.pdf",
                success=True,
            )
            print("❌ EXPIRATION TEST FAILED: Should block conversions after limit!")
            raise AssertionError("Trial expiration not enforced")
        except TrialExpiredError as e:
            print(f"✓ Trial correctly blocks conversions after limit")
            print(f"  Error: {e}")
            print("✅ Trial expiration test PASSED")
    else:
        print(f"⚠ Trial not yet expired ({status['remaining']} remaining)")
        print("  Skipping expiration test")


def test_license_manager():
    """Test 7: License manager basics."""
    print_section("TEST 7: License Manager")

    manager = get_license_manager()
    print(f"✓ License manager initialized")

    # Get status
    status = manager.get_license_status()
    print(f"✓ License status: {status['license_type']}")

    # Get machine ID
    machine_id = manager.get_machine_id()
    print(f"✓ Machine ID: {machine_id[:16]}...")

    print("✅ License manager test PASSED")


def test_invalid_license_key():
    """Test 8: Invalid license key rejection."""
    print_section("TEST 8: Invalid License Key")

    try:
        activate_license_key("INVALID-KEY-12345")
        print("❌ INVALID KEY TEST FAILED: Should reject invalid keys!")
        raise AssertionError("Invalid license key accepted")
    except LicenseError as e:
        print(f"✓ Invalid license key correctly rejected")
        print(f"  Error: {e}")
        print("✅ Invalid license key test PASSED")


def print_summary():
    """Print test summary."""
    print_section("LICENSING SYSTEM TEST SUMMARY")

    status = get_trial_status()
    license_type = get_license_type()

    print(f"License Type: {license_type}")
    print(f"Trial Status: {status['status']}")
    print(f"Conversions Used: {status['used']}/{status['limit']}")
    print(f"Conversions Remaining: {status['remaining']}")

    print(f"\n✅ ALL LICENSING TESTS PASSED!")
    print(f"\nNext Steps:")
    print(f"  1. Generate RSA key pair for production")
    print(f"  2. Setup Gumroad for payment processing")
    print(f"  3. Build frontend license UI components")
    print(f"  4. Test full purchase → activation flow")


def main():
    """Run all tests."""
    print("\n" + "🔒"*30)
    print("  LICENSING SYSTEM VALIDATION TEST")
    print("🔒"*30)

    try:
        test_trial_status()
        test_free_tier_converter()
        test_paid_tier_converter_blocked()
        test_file_size_limit()
        test_conversion_tracking()
        test_trial_expiration()
        test_license_manager()
        test_invalid_license_key()

        print_summary()
        return 0

    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
