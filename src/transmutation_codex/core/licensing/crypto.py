"""Cryptographic functions for license validation.

This module provides RSA-based license key validation for offline operation.
License keys are signed with a private key (kept secret) and verified using
a public key (embedded in the application).
"""

import base64
import hashlib
import json
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class LicenseCrypto:
    """Handle license key generation and validation using RSA signatures."""

    def __init__(self):
        """Initialize crypto handler with embedded public key."""
        # Public key (embedded in application)
        # Generated via scripts/generate_rsa_keys.py
        self._public_key_pem = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxF8GdEKu3EJubH+Guvuo
h1YD0ITzMr20aZpQzvi8iLfjORhK8C6nWEozX/r1o0MnjhVEKWNKaHaSYo4ZlSwV
IByxa8QEJ0hmI03xzKhrgFoxq/Lcpz+ED5SzsI59VUd/3MrkwjqaclkUndjFKcLS
+/Qpr6+yKl8AOFMD+X1Kn98kKjHpHaPL4EmjF8FIESKSSVSay14tN5USd9s72PRb
Ij84jWA5nBf0DTosptCTL4+TLJUFqWh0O7uva2JMr+mHcviJQPdWv1XIUqph0kfd
4w2LmyF+rftTGyaoIzxALbBbFwl5SkCAVoEm/DRMzDMwxhS7njZk0TKvSk9cpdIf
tQIDAQAB
-----END PUBLIC KEY-----"""

    def validate_license_key(self, license_key: str) -> dict[str, Any] | None:
        """Validate a license key and extract its data.

        Args:
            license_key: License key in format "KEY:SIGNATURE:DATA"

        Returns:
            Dictionary containing license data if valid, None if invalid

        Example:
            >>> crypto = LicenseCrypto()
            >>> data = crypto.validate_license_key("AICHEMIST-XXXXX-...")
            >>> if data:
            ...     print(f"License valid for {data['email']}")
        """
        try:
            # Parse license key format: PREFIX:SIGNATURE:DATA
            parts = license_key.split(":")
            if len(parts) != 3:
                return None

            prefix, signature_b64, data_b64 = parts

            # Verify prefix
            if prefix != "AICHEMIST":
                return None

            # Decode signature and data
            signature = base64.b64decode(signature_b64)
            data_json = base64.b64decode(data_b64)

            # Load public key
            public_key = serialization.load_pem_public_key(self._public_key_pem)

            # Verify signature
            public_key.verify(
                signature,
                data_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Parse and return license data
            license_data = json.loads(data_json.decode("utf-8"))
            return license_data

        except (InvalidSignature, ValueError, KeyError, json.JSONDecodeError):
            return None

    def generate_license_key(
        self, license_data: dict[str, Any], private_key_pem: bytes
    ) -> str:
        """Generate a signed license key (for internal use only).

        Args:
            license_data: Dictionary containing license information
            private_key_pem: PEM-encoded private key

        Returns:
            License key string in format "AICHEMIST:SIGNATURE:DATA"

        Note:
            This function should only be used by the license generation service,
            NOT in the client application.
        """
        # Serialize license data
        data_json = json.dumps(license_data, sort_keys=True).encode("utf-8")

        # Load private key
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)

        # Sign data
        signature = private_key.sign(
            data_json,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        # Encode to base64
        signature_b64 = base64.b64encode(signature).decode("utf-8")
        data_b64 = base64.b64encode(data_json).decode("utf-8")

        # Format: PREFIX:SIGNATURE:DATA
        return f"AICHEMIST:{signature_b64}:{data_b64}"

    @staticmethod
    def generate_key_pair() -> tuple[bytes, bytes]:
        """Generate a new RSA key pair for license signing.

        Returns:
            Tuple of (private_key_pem, public_key_pem)

        Note:
            This should only be run once during initial setup.
            The private key must be kept secret and secure.
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    @staticmethod
    def hash_machine_id(machine_id: str) -> str:
        """Create a consistent hash of machine ID for license binding.

        Args:
            machine_id: Unique machine identifier

        Returns:
            SHA256 hash of machine ID
        """
        return hashlib.sha256(machine_id.encode("utf-8")).hexdigest()
