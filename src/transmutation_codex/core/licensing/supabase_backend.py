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

    def validate_license_online(
        self, license_key: str
    ) -> tuple[bool, dict[str, Any] | None, str]:
        """Validate license key against Supabase backend.

        Args:
            license_key: License key to validate

        Returns:
            Tuple of (is_valid, license_data, reason)
            - is_valid: Whether license is valid
            - license_data: License information if valid
            - reason: Reason for validation result

        Example:
            >>> backend = SupabaseBackend()
            >>> valid, data, reason = backend.validate_license_online("AICHEMIST-...")
            >>> if valid:
            ...     print(f"License for {data['email']} is valid")
        """
        try:
            # Query licenses table
            response = self.client.table("licenses").select("*").eq(
                "license_key", license_key
            ).single().execute()

            if not response.data:
                return False, None, "License key not found"

            license_data = response.data

            # Check license status
            if license_data.get("status") != "active":
                return False, None, f"License status: {license_data.get('status')}"

            # Check expiration
            expires_at = license_data.get("expires_at")
            if expires_at:
                expiry_date = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if expiry_date < datetime.now(expiry_date.tzinfo):
                    return False, None, "License expired"

            # Cache result
            self._cache[license_key] = {
                "data": license_data,
                "cached_at": datetime.now(),
            }

            return True, license_data, "Valid"

        except Exception as e:
            # Check cache for offline operation
            cached = self._cache.get(license_key)
            if cached:
                cache_age = datetime.now() - cached["cached_at"]
                if cache_age < self._cache_ttl:
                    return True, cached["data"], "Valid (cached)"

            return False, None, f"Validation error: {str(e)}"

    def record_activation(
        self,
        license_id: int | str,
        machine_id: str | None = None,
    ) -> tuple[bool, str]:
        """Record a license activation.

        Args:
            license_id: ID of the license from licenses table
            machine_id: Machine fingerprint (auto-generated if not provided)

        Returns:
            Tuple of (success, message)

        Example:
            >>> backend = SupabaseBackend()
            >>> success, msg = backend.record_activation(123, "machine-hash")
        """
        if machine_id is None:
            machine_id = self.fingerprint.get_machine_id()

        try:
            # Check if already activated on this machine
            existing = self.client.table("activations").select("*").eq(
                "license_id", license_id
            ).eq("machine_id", machine_id).execute()

            if existing.data:
                # Update last_seen_at
                self.client.table("activations").update({
                    "last_seen_at": datetime.now().isoformat()
                }).eq("id", existing.data[0]["id"]).execute()
                return True, "Activation updated"

            # Check max activations
            license_data = self.client.table("licenses").select("*").eq(
                "id", license_id
            ).single().execute()

            if not license_data.data:
                return False, "License not found"

            max_activations = license_data.data.get("max_activations", 1)

            # Count current activations
            all_activations = self.client.table("activations").select("*").eq(
                "license_id", license_id
            ).execute()

            if len(all_activations.data) >= max_activations:
                return False, f"Maximum activations ({max_activations}) reached"

            # Create new activation
            self.client.table("activations").insert({
                "license_id": license_id,
                "machine_id": machine_id,
                "activated_at": datetime.now().isoformat(),
                "last_seen_at": datetime.now().isoformat(),
            }).execute()

            return True, "Activation recorded"

        except Exception as e:
            return False, f"Activation error: {str(e)}"

    def log_usage(
        self,
        license_id: int | str,
        converter_name: str,
        input_file_size: int,
        success: bool = True,
    ) -> bool:
        """Log a conversion usage event.

        Args:
            license_id: ID of the license
            converter_name: Name of converter used
            input_file_size: Size of input file in bytes
            success: Whether conversion succeeded

        Returns:
            True if logged successfully

        Example:
            >>> backend = SupabaseBackend()
            >>> backend.log_usage(123, "md2pdf", 1024000, True)
        """
        try:
            self.client.table("usage_logs").insert({
                "license_id": license_id,
                "converter_name": converter_name,
                "input_file_size": input_file_size,
                "success": success,
                "created_at": datetime.now().isoformat(),
            }).execute()
            return True

        except Exception as e:
            # Non-critical - don't fail conversion on logging error
            print(f"Usage logging failed: {e}")
            return False

    def check_license_status(
        self, license_key: str
    ) -> dict[str, Any]:
        """Get comprehensive license status from Supabase.

        Args:
            license_key: License key to check

        Returns:
            Dictionary with license status information

        Example:
            >>> backend = SupabaseBackend()
            >>> status = backend.check_license_status("AICHEMIST-...")
            >>> print(f"Status: {status['status']}")
        """
        valid, data, reason = self.validate_license_online(license_key)

        if not valid:
            return {
                "valid": False,
                "reason": reason,
                "status": "invalid",
            }

        # Get activation count
        activations = self.client.table("activations").select("*").eq(
            "license_id", data["id"]
        ).execute()

        # Get usage stats
        usage = self.client.table("usage_logs").select("*").eq(
            "license_id", data["id"]
        ).execute()

        return {
            "valid": True,
            "status": data.get("status"),
            "email": data.get("email"),
            "license_type": data.get("type"),
            "max_activations": data.get("max_activations"),
            "current_activations": len(activations.data) if activations.data else 0,
            "total_conversions": len(usage.data) if usage.data else 0,
            "created_at": data.get("created_at"),
            "expires_at": data.get("expires_at"),
        }

    def deactivate_machine(
        self, license_id: int | str, machine_id: str | None = None
    ) -> tuple[bool, str]:
        """Deactivate a license from a specific machine.

        Args:
            license_id: ID of the license
            machine_id: Machine to deactivate (current machine if not provided)

        Returns:
            Tuple of (success, message)
        """
        if machine_id is None:
            machine_id = self.fingerprint.get_machine_id()

        try:
            result = self.client.table("activations").delete().eq(
                "license_id", license_id
            ).eq("machine_id", machine_id).execute()

            if result.data:
                return True, "Machine deactivated"
            return False, "Activation not found"

        except Exception as e:
            return False, f"Deactivation error: {str(e)}"

    def get_activation_list(self, license_id: int | str) -> list[dict[str, Any]]:
        """Get list of all activations for a license.

        Args:
            license_id: ID of the license

        Returns:
            List of activation records

        Example:
            >>> backend = SupabaseBackend()
            >>> activations = backend.get_activation_list(123)
            >>> for act in activations:
            ...     print(f"Machine: {act['machine_id'][:8]}...")
        """
        try:
            response = self.client.table("activations").select("*").eq(
                "license_id", license_id
            ).order("activated_at", desc=True).execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"Failed to fetch activations: {e}")
            return []

    def is_online_available(self) -> bool:
        """Check if Supabase backend is available.

        Returns:
            True if can connect to Supabase

        Example:
            >>> backend = SupabaseBackend()
            >>> if backend.is_online_available():
            ...     # Use online validation
        """
        try:
            # Simple health check
            self.client.table("licenses").select("id").limit(1).execute()
            return True
        except Exception:
            return False


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
