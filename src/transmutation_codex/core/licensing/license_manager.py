"""License management and validation.

This module provides the main LicenseManager class that coordinates
license validation, storage, and activation using Gumroad's license API.
Supports offline caching with optional Supabase backend for enhanced features.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests

from ..exceptions import LicenseError
from .activation import ActivationManager, MachineFingerprint
from .trial_manager import TrialManager

# Optional Supabase backend
try:
    from .supabase_backend import SupabaseBackend, is_supabase_configured

    SUPABASE_AVAILABLE = True
except (ImportError, ValueError):
    SUPABASE_AVAILABLE = False
    SupabaseBackend = None  # type: ignore

    def is_supabase_configured() -> bool:  # type: ignore
        """Stub function when Supabase is not available."""
        return False


class GumroadLicenseVerifier:
    """Handle license verification with Gumroad API."""

    def __init__(self):
        """Initialize Gumroad API client."""
        self.api_base = "https://api.gumroad.com/v2"
        self.session = requests.Session()
        self.session.timeout = 10  # 10 second timeout

    def verify_license(self, license_key: str, product_id: str) -> dict[str, Any]:
        """Verify a license key with Gumroad API.

        Args:
            license_key: The license key from Gumroad
            product_id: Gumroad product ID (not permalink)

        Returns:
            License verification data from Gumroad

        Raises:
            LicenseError: If verification fails

        Example:
            >>> verifier = GumroadLicenseVerifier()
            >>> data = verifier.verify_license("ABC123", "product-id")
            >>> print(f"License valid: {data['success']}")
        """
        url = f"{self.api_base}/licenses/verify"

        data = {
            "product_id": product_id,
            "license_key": license_key,
            "increment_uses_count": "false",  # Don't increment on verification
        }

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise LicenseError(
                    "Invalid license key",
                    license_type="gumroad",
                    reason="verification_failed",
                )

            return result

        except requests.RequestException as e:
            raise LicenseError(
                f"Failed to verify license with Gumroad: {e}",
                license_type="gumroad",
                reason="api_error",
            )


class LicenseManager:
    """Central license management system using Gumroad API."""

    # Product ID mapping for different tiers (actual Gumroad product IDs)
    # Get product IDs from: Gumroad Dashboard → Product → Content tab → "Use your product ID to verify licenses through the API"
    PRODUCT_MAPPING = {
        "basic": "E7oYHqtGSVBBWcpbCFyF-A==",  # AiChemist Transmutation Codex (current product)
        "pro": "E7oYHqtGSVBBWcpbCFyF-A==",  # TODO: Update when Pro tier product is created
        "enterprise": "E7oYHqtGSVBBWcpbCFyF-A==",  # TODO: Update when Enterprise tier product is created
    }

    def __init__(self, data_dir: Path | None = None):
        """Initialize license manager.

        Args:
            data_dir: Directory for storing license data
                     Defaults to platform-specific AppData:
                     - Windows: %APPDATA%/AiChemist
                     - macOS: ~/Library/Application Support/AiChemist
                     - Linux: ~/.local/share/aichemist

        Example:
            >>> manager = LicenseManager()
            >>> status = manager.get_license_status()
            >>> print(f"License type: {status['license_type']}")
        """
        if data_dir is None:
            # Use platform-specific application data directory
            data_dir = self._get_app_data_dir()

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # License file path
        self.license_file = self.data_dir / "gumroad_license.json"

        # Cache file for API responses
        self.cache_file = self.data_dir / "license_cache.json"

        # Initialize components
        self.verifier = GumroadLicenseVerifier()
        self.activation_manager = ActivationManager(self.license_file)
        self.trial_manager = TrialManager(self.data_dir)

        # Initialize Supabase backend if configured
        self.supabase_backend = None
        if SUPABASE_AVAILABLE and is_supabase_configured():
            try:
                self.supabase_backend = SupabaseBackend()
            except Exception:
                # Supabase not available - fall back to offline mode
                self.supabase_backend = None

        # Load current license
        self._current_license = self._load_license()
        self._license_cache = self._load_cache()

    @staticmethod
    def _get_app_data_dir() -> Path:
        """Get platform-specific application data directory.

        Returns platform-appropriate paths:
        - Windows: %APPDATA%/AiChemist
        - macOS: ~/Library/Application Support/AiChemist
        - Linux: ~/.local/share/aichemist

        Returns:
            Path: Application data directory path.
        """
        import platform

        system = platform.system()

        if system == "Windows":
            # Windows: Use APPDATA environment variable
            appdata = os.getenv("APPDATA")
            if appdata:
                return Path(appdata) / "AiChemist"
            # Fallback to user profile
            return Path.home() / "AppData" / "Roaming" / "AiChemist"

        elif system == "Darwin":
            # macOS: Use Application Support
            return Path.home() / "Library" / "Application Support" / "AiChemist"

        else:
            # Linux and others: Use XDG_DATA_HOME or fallback to ~/.local/share
            xdg_data_home = os.getenv("XDG_DATA_HOME")
            if xdg_data_home:
                return Path(xdg_data_home) / "aichemist"
            return Path.home() / ".local" / "share" / "aichemist"

    def _load_license(self) -> dict[str, Any] | None:
        """Load license from disk.

        Returns:
            License data if valid license exists, None otherwise
        """
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file) as f:
                license_data = json.load(f)

            # Validate machine binding
            if not self.activation_manager.is_activated_on_this_machine(license_data):
                return None

            return license_data

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return None

    def _load_cache(self) -> dict[str, Any]:
        """Load license cache from disk.

        Returns:
            Cached license verification data
        """
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file) as f:
                cache = json.load(f)

            # Clean expired cache entries
            now = datetime.now()
            valid_cache = {}

            for key, data in cache.items():
                if "cached_at" in data:
                    cached_time = datetime.fromisoformat(data["cached_at"])
                    # Cache for 24 hours
                    if now - cached_time < timedelta(hours=24):
                        valid_cache[key] = data

            return valid_cache

        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_cache(self):
        """Save license cache to disk."""
        with open(self.cache_file, "w") as f:
            json.dump(self._license_cache, f, indent=2, default=str)

    def _save_license(self, license_data: dict[str, Any]):
        """Save license to disk.

        Args:
            license_data: License data to save
        """
        with open(self.license_file, "w") as f:
            json.dump(license_data, f, indent=2, default=str)

        self._current_license = license_data

    def activate_license(self, license_key: str) -> dict[str, Any]:
        """Activate a Gumroad license key.

        Verifies the license key with Gumroad API and activates it locally.
        Uses caching to avoid repeated API calls.

        Args:
            license_key: Gumroad license key to activate

        Returns:
            License status after activation

        Raises:
            LicenseError: If license key is invalid or cannot be activated

        Example:
            >>> manager = LicenseManager()
            >>> status = manager.activate_license("ABC123-DEF456")
            >>> print(f"Activated: {status['activated']}")
        """
        cache_key = f"verify_{license_key}"

        # Check cache first (avoid repeated API calls)
        if cache_key in self._license_cache:
            cached_data = self._license_cache[cache_key]
            gumroad_data = cached_data.get("gumroad_data")
        else:
            # Verify with Gumroad API for all known product IDs
            gumroad_data = None
            last_error = None

            for tier, product_id in self.PRODUCT_MAPPING.items():
                try:
                    result = self.verifier.verify_license(license_key, product_id)
                    if result.get("success"):
                        gumroad_data = result
                        gumroad_data["detected_tier"] = tier
                        break
                except LicenseError as e:
                    last_error = e
                    continue

            if not gumroad_data:
                error_msg = "Invalid license key - not found for any product"
                if last_error:
                    error_msg += f": {last_error}"
                raise LicenseError(
                    error_msg,
                    license_type="gumroad",
                    reason="validation_failed",
                )

            # Cache the verification result
            self._license_cache[cache_key] = {
                "gumroad_data": gumroad_data,
                "cached_at": datetime.now().isoformat(),
            }
            self._save_cache()

        # Check if license is refunded or disputed
        purchase = gumroad_data.get("purchase", {})
        if purchase.get("refunded") or purchase.get("disputed"):
            raise LicenseError(
                "License has been refunded or disputed",
                license_type="gumroad",
                reason="license_revoked",
            )

        # Determine license tier from purchase data
        detected_tier = gumroad_data.get("detected_tier", "basic")
        license_type = detected_tier

        # Create license data structure
        license_data = {
            "license_type": license_type,
            "license_key": license_key,
            "gumroad_data": gumroad_data,
            "email": purchase.get("email", ""),
            "purchase_id": purchase.get("id", ""),
            "product_name": purchase.get("product_name", ""),
            "max_activations": self._get_max_activations_for_tier(license_type),
            "activation_date": datetime.now().isoformat(),
            "validation_mode": "gumroad_api",
        }

        # Check activation limits
        can_activate, reason = self.activation_manager.can_activate(license_data)
        if not can_activate:
            raise LicenseError(
                f"Cannot activate license: {reason}",
                license_type=license_type,
                reason="activation_failed",
            )

        # Activate license locally
        activated_license = self.activation_manager.activate_license(license_data)

        # Save to disk
        self._save_license(activated_license)

        # Record in Supabase if available
        if self.supabase_backend and gumroad_data:
            try:
                self.supabase_backend.record_gumroad_activation(
                    license_key=license_key,
                    gumroad_data=gumroad_data,
                    tier=license_type,
                )
            except Exception:
                # Non-critical - don't fail activation on logging error
                pass

        return self.get_license_status()

    def _get_max_activations_for_tier(self, tier: str) -> int:
        """Get maximum activations allowed for a license tier.

        Args:
            tier: License tier (basic, pro, enterprise)

        Returns:
            Maximum number of device activations allowed
        """
        tier_limits = {"basic": 1, "pro": 3, "enterprise": 10}
        return tier_limits.get(tier, 1)

    def deactivate_license(self) -> dict[str, Any]:
        """Deactivate current license.

        Returns:
            License status after deactivation

        Raises:
            LicenseError: If no active license exists
        """
        if not self._current_license:
            raise LicenseError(
                "No active license to deactivate",
                license_type="none",
                reason="no_license",
            )

        # Record deactivation in Supabase if available
        if self.supabase_backend and self._current_license:
            try:
                license_key = self._current_license.get("license_key")
                if license_key:
                    self.supabase_backend.record_deactivation(license_key)
            except Exception:
                # Non-critical - continue with deactivation
                pass

        # Remove license file
        if self.license_file.exists():
            self.license_file.unlink()

        self._current_license = None

        return self.get_license_status()

    def get_license_status(self) -> dict[str, Any]:
        """Get current license status.

        Returns:
            Dictionary with license information:
            - license_type: "trial" | "basic" | "pro" | "enterprise"
            - activated: Whether a paid license is activated
            - trial_status: Trial information (if applicable)
            - email: License holder email (if paid)
            - tier: License tier (if paid)
            - product_name: Gumroad product name (if paid)

        Example:
            >>> manager = LicenseManager()
            >>> status = manager.get_license_status()
            >>> if status["license_type"] == "trial":
            ...     print(f"Trial: {status['trial_status']['remaining']} left")
        """
        if self._current_license:
            # Paid license active
            license_type = self._current_license.get("license_type", "basic")
            return {
                "license_type": license_type,
                "activated": True,
                "email": self._current_license.get("email"),
                "tier": license_type,
                "product_name": self._current_license.get("product_name"),
                "purchase_id": self._current_license.get("purchase_id"),
                "activation_date": self._current_license.get("activation_date"),
                "validation_mode": self._current_license.get("validation_mode"),
                "max_activations": self._current_license.get("max_activations"),
            }

        # No paid license - fall back to trial
        trial_status = self.trial_manager.get_trial_status()

        return {
            "license_type": "trial",
            "activated": False,
            "trial_status": trial_status,
        }

    def has_feature_access(self, feature: str) -> bool:
        """Check if current license allows access to a feature.

        Args:
            feature: Feature name to check

        Returns:
            True if feature is accessible

        Example:
            >>> manager = LicenseManager()
            >>> if manager.has_feature_access("pdf2md"):
            ...     # Perform conversion
        """
        status = self.get_license_status()
        license_type = status.get("license_type", "trial")

        if license_type in ["basic", "pro", "enterprise"]:
            # All paid tiers have access to all features
            # Future: could implement feature restrictions per tier
            return True

        # Trial license - limited features
        return feature in self.trial_manager.FREE_CONVERTERS

    def check_file_size_limit(self, file_path: str) -> tuple[bool, int]:
        """Check if file size is within license limits.

        Args:
            file_path: Path to file to check

        Returns:
            Tuple of (allowed, limit_bytes)
            - allowed: Whether file size is allowed
            - limit_bytes: Maximum file size for current license

        Raises:
            LicenseError: If file exceeds size limit
        """
        file_size = Path(file_path).stat().st_size

        status = self.get_license_status()
        license_type = status.get("license_type", "trial")

        if license_type in ["basic", "pro", "enterprise"]:
            # Paid licenses - no file size limit
            return True, -1

        # Trial license - 5MB limit
        limit_bytes = 5 * 1024 * 1024  # 5 MB

        if file_size > limit_bytes:
            raise LicenseError(
                f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds "
                f"trial limit ({limit_bytes / 1024 / 1024:.1f} MB). "
                "Please upgrade to remove file size limits.",
                license_type="trial",
                reason="file_size_limit",
            )

        return True, limit_bytes

    def record_conversion(self, converter_name: str, input_file: str, **kwargs):
        """Record a conversion (for trial tracking and usage analytics).

        Args:
            converter_name: Name of converter used
            input_file: Input file path
            **kwargs: Additional conversion metadata (output_file, file_size_bytes, success)
        """
        status = self.get_license_status()
        license_type = status.get("license_type", "trial")
        file_size_bytes = kwargs.get("file_size_bytes", 0)

        if license_type == "trial":
            # Record for trial tracking
            self.trial_manager.record_conversion(
                converter_name=converter_name,
                input_file=input_file,
                output_file=kwargs.get("output_file"),
                file_size_bytes=file_size_bytes,
                success=kwargs.get("success", True),
            )
        elif license_type in ["basic", "pro", "enterprise"] and self.supabase_backend:
            # Log usage to Supabase for paid licenses
            try:
                if self._current_license and "license_key" in self._current_license:
                    license_key = self._current_license.get("license_key")
                    if license_key:
                        self.supabase_backend.log_gumroad_usage(
                            license_key=license_key,
                            converter_name=converter_name,
                            input_file_size=file_size_bytes,
                            success=kwargs.get("success", True),
                        )
            except Exception:
                # Non-critical - don't fail conversion on logging error
                pass

    def get_machine_id(self) -> str:
        """Get current machine ID (for support/debugging).

        Returns:
            Machine ID string
        """
        return MachineFingerprint.get_machine_id()
