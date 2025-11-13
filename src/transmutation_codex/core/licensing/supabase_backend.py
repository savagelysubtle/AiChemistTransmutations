"""Supabase backend for cloud-based license validation.

This module provides online license validation, activation tracking,
and usage analytics through Supabase backend. It complements the
offline RSA-based validation system.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load from project root
    env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # python-dotenv not installed

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None  # type: ignore

from ..exceptions import LicenseError
from .activation import MachineFingerprint


class SupabaseBackend:
    """Cloud-based license validation and tracking using Supabase."""

    def __init__(self):
        """Initialize Supabase client.

        Raises:
            ImportError: If supabase-py is not installed
            ValueError: If Supabase credentials are not configured
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "supabase-py is not installed. "
                "Install with: pip install supabase"
            )

        # Load Supabase credentials from environment
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")

        if not url or not key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )

        self.client: Client = create_client(url, key)
        self.fingerprint = MachineFingerprint()

        # Cache for offline operation
        self._cache: dict[str, Any] = {}
        self._cache_ttl = timedelta(hours=24)

    def record_gumroad_activation(
        self, license_key: str, gumroad_data: dict[str, Any], tier: str
    ) -> bool:
        """Record a Gumroad license activation in Supabase.

        Args:
            license_key: The Gumroad license key
            gumroad_data: Full Gumroad API response data
            tier: License tier (basic, pro, enterprise)

        Returns:
            True if recorded successfully

        Raises:
            LicenseError: If recording fails
        """
        try:
            purchase = gumroad_data.get('purchase', {})
            machine_id = self.fingerprint.get_machine_id()

            # Prepare license data for Supabase
            license_data = {
                "license_key": license_key,
                "gumroad_purchase_id": purchase.get('id'),
                "gumroad_product_id": purchase.get('product_id'),
                "tier": tier,
                "email": purchase.get('email', ''),
                "purchase_date": purchase.get('sale_timestamp'),
                "activation_date": datetime.now().isoformat(),
                "machine_id": machine_id,
                "gumroad_data": gumroad_data,
                "status": "active",
                "max_activations": self._get_max_activations_for_tier(tier),
            }

            # Insert or update license record
            response = self.client.table("gumroad_licenses").upsert(
                license_data,
                on_conflict="license_key"
            ).execute()

            return True

        except Exception as e:
            raise LicenseError(
                f"Failed to record Gumroad activation: {e}",
                license_type="gumroad",
                reason="supabase_error"
            )

    def record_deactivation(self, license_key: str) -> bool:
        """Record license deactivation in Supabase.

        Args:
            license_key: The license key being deactivated

        Returns:
            True if recorded successfully
        """
        try:
            # Update deactivation date
            self.client.table("gumroad_licenses").update({
                "deactivation_date": datetime.now().isoformat(),
                "status": "deactivated"
            }).eq("license_key", license_key).execute()

            return True
        except Exception:
            # Non-critical - don't fail deactivation
            return False

    def log_gumroad_usage(
        self,
        license_key: str,
        converter_name: str,
        input_file_size: int,
        success: bool
    ) -> bool:
        """Log conversion usage for Gumroad licenses.

        Args:
            license_key: The Gumroad license key
            converter_name: Name of converter used
            input_file_size: Size of input file in bytes
            success: Whether conversion succeeded

        Returns:
            True if logged successfully
        """
        try:
            usage_data = {
                "license_key": license_key,
                "converter_name": converter_name,
                "input_file_size": input_file_size,
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "machine_id": self.fingerprint.get_machine_id(),
            }

            self.client.table("gumroad_usage").insert(usage_data).execute()
            return True
        except Exception:
            # Non-critical - don't fail conversion
            return False

    def _get_max_activations_for_tier(self, tier: str) -> int:
        """Get maximum activations for a tier."""
        tier_limits = {
            "basic": 1,
            "pro": 3,
            "enterprise": 10
        }
        return tier_limits.get(tier, 1)


def is_supabase_configured() -> bool:
    """Check if Supabase is configured in environment.

    Returns:
        True if SUPABASE_URL and SUPABASE_ANON_KEY are set

    Example:
        >>> if is_supabase_configured():
        ...     backend = SupabaseBackend()
    """
    return bool(
        os.getenv("SUPABASE_URL") and
        os.getenv("SUPABASE_ANON_KEY") and
        SUPABASE_AVAILABLE
    )
