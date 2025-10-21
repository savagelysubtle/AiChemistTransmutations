"""Generate RSA key pair for license signing.

This script should be run ONCE during initial setup to generate the public/private
key pair used for license validation.

SECURITY WARNING:
- The private key must be kept SECRET and SECURE
- Only the public key should be embedded in the application
- Store the private key in a secure location (password manager, HSM, etc.)
- Never commit the private key to version control
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transmutation_codex.core.licensing.crypto import LicenseCrypto


def main():
    """Generate and save RSA key pair."""
    print("Generating RSA-2048 key pair for license signing...")
    print()

    # Generate keys
    private_key, public_key = LicenseCrypto.generate_key_pair()

    # Save to secure location
    keys_dir = Path(__file__).parent / "keys"
    keys_dir.mkdir(exist_ok=True)

    private_key_path = keys_dir / "private_key.pem"
    public_key_path = keys_dir / "public_key.pem"

    # Write private key
    with open(private_key_path, "wb") as f:
        f.write(private_key)

    # Write public key
    with open(public_key_path, "wb") as f:
        f.write(public_key)

    print("✅ Key pair generated successfully!")
    print()
    print(f"Private key saved to: {private_key_path}")
    print(f"Public key saved to: {public_key_path}")
    print()
    print("=" * 70)
    print("IMPORTANT: Next Steps")
    print("=" * 70)
    print()
    print("1. SECURE THE PRIVATE KEY:")
    print(f"   - Move {private_key_path} to a secure location")
    print("   - Store in password manager or hardware security module (HSM)")
    print("   - Add scripts/keys/ to .gitignore to prevent accidental commits")
    print()
    print("2. UPDATE PUBLIC KEY IN APPLICATION:")
    print(f"   - Copy the contents of {public_key_path}")
    print("   - Replace the placeholder public key in:")
    print("     src/transmutation_codex/core/licensing/crypto.py")
    print("   - Look for '_public_key_pem = b\"\"\"-----BEGIN PUBLIC KEY-----'")
    print()
    print("3. TEST LICENSE GENERATION:")
    print("   - Run: python scripts/generate_license.py")
    print("   - Use the test license to verify activation works")
    print()
    print("=" * 70)
    print()
    print("PUBLIC KEY (copy this to crypto.py):")
    print("=" * 70)
    print(public_key.decode("utf-8"))
    print("=" * 70)


if __name__ == "__main__":
    main()
