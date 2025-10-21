"""Quick license generator without Supabase dependency.

Generates a license key using the existing RSA private key.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transmutation_codex.core.licensing.crypto import LicenseCrypto


def main():
    """Generate a dev license key."""
    print("=" * 80)
    print("AICHEMIST DEV LICENSE GENERATOR")
    print("=" * 80)

    # Load private key
    private_key_path = Path(__file__).parent / "keys" / "private_key.pem"

    if not private_key_path.exists():
        print(f"\nERROR: Private key not found at: {private_key_path}")
        print("Run: python scripts/generate_rsa_keys.py")
        sys.exit(1)

    print(f"\nLoading private key from: {private_key_path}")
    with open(private_key_path, "rb") as f:
        private_key_pem = f.read()

    # Prepare dev license data
    license_data = {
        "email": "dev@aichemist.local",
        "license_type": "enterprise",
        "max_activations": 999,
        "features": ["all"],
        "issued_at": datetime.now().isoformat(),
    }

    # Generate license key
    crypto = LicenseCrypto()
    license_key = crypto.generate_license_key(license_data, private_key_pem)

    print("\n" + "=" * 80)
    print("GENERATED DEV LICENSE KEY:")
    print("=" * 80)
    print(f"\n{license_key}\n")
    print("=" * 80)

    print("\nLICENSE DETAILS:")
    print(f"- Email: {license_data['email']}")
    print(f"- Type: {license_data['license_type']}")
    print(f"- Max Activations: {license_data['max_activations']}")
    print("- Expires: Never (Perpetual)")
    print("- Features: All converters unlocked")

    # Save to file
    output_file = Path(__file__).parent.parent / "DEV_LICENSE.txt"
    with open(output_file, "w") as f:
        f.write("AiChemist Development License\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"LICENSE KEY:\n{license_key}\n\n")
        f.write(f"Email: {license_data['email']}\n")
        f.write(f"Type: {license_data['license_type']}\n")
        f.write(f"Max Activations: {license_data['max_activations']}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"\n✓ License saved to: {output_file}")
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("\n1. Test license activation in GUI:")
    print("   - cd gui && npm run dev")
    print("   - Click 'Activate License'")
    print(f"   - Enter: {license_key[:50]}...")
    print("\n2. Or test from command line:")
    print("   - python tests/test_licensing_system.py")
    print("\n3. To insert into Supabase:")
    print("   - Execute scripts/supabase_setup.sql in Supabase Dashboard")
    print("   - Then run: python scripts/generate_dev_license.py")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
