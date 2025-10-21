"""License management and validation.

This module provides the main LicenseManager class that coordinates
license validation, storage, and activation. Supports both offline
(RSA-based) and online (Supabase-based) validation modes.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from ..exceptions import LicenseError
from .activation import ActivationManager, MachineFingerprint
from .crypto import LicenseCrypto
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


class LicenseManager:
    """Central license management system."""

    def __init__(self, data_dir: Path | None = None):
        """Initialize license manager.

        Args:
            data_dir: Directory for storing license data
                     Defaults to ~/.aichemist or %APPDATA%/AiChemist

        Example:
            >>> manager = LicenseManager()
            >>> status = manager.get_license_status()
            >>> print(f"License type: {status['license_type']}")
        """
        if data_dir is None:
            # Default data directory
            if Path.home().joinpath(".aichemist").exists():
                data_dir = Path.home() / ".aichemist"
            else:
                # Windows AppData
                import os

                appdata = os.getenv("APPDATA")
                if appdata:
                    data_dir = Path(appdata) / "AiChemist"
                else:
                    data_dir = Path.home() / ".aichemist"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # License file path
        self.license_file = self.data_dir / "license.json"

        # Initialize components
        self.crypto = LicenseCrypto()
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

    def _load_license(self) -> dict | None:
        """Load license from disk.

        Returns:
            License data if valid license exists, None otherwise
        """
        if not self.license_file.exists():
            return None

        try:
            with open(self.license_file, "r") as f:
                license_data = json.load(f)

            # Validate machine binding
            if not self.activation_manager.is_activated_on_this_machine(license_data):
                return None

            return license_data

        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return None

    def _save_license(self, license_data: dict):
        """Save license to disk.

        Args:
            license_data: License data to save
        """
        with open(self.license_file, "w") as f:
            json.dump(license_data, f, indent=2)

        self._current_license = license_data

    def activate_license(self, license_key: str) -> dict:
        """Activate a license key.

        Tries online validation first (if Supabase configured), then falls back
        to offline RSA validation.

        Args:
            license_key: License key to activate

        Returns:
            License status after activation

        Raises:
            LicenseError: If license key is invalid or cannot be activated

        Example:
            >>> manager = LicenseManager()
            >>> status = manager.activate_license("AICHEMIST-XXXXX-...")
            >>> print(f"Activated: {status['activated']}")
        """
        license_data = None
        validation_mode = "offline"

        # Try online validation first
        if self.supabase_backend and self.supabase_backend.is_online_available():
            try:
                valid, online_data, reason = self.supabase_backend.validate_license_online(
                    license_key
                )
                if valid and online_data:
                    license_data = online_data
                    validation_mode = "online"
                    # Record activation in Supabase
                    success, msg = self.supabase_backend.record_activation(
                        online_data["id"]
                    )
                    if not success:
                        # Warning but don't fail - offline will handle it
                        pass
            except Exception:
                # Fall through to offline validation
                pass

        # Fall back to offline RSA validation
        if not license_data:
            license_data = self.crypto.validate_license_key(license_key)
            validation_mode = "offline"

        if not license_data:
            raise LicenseError(
                "Invalid license key",
                license_type="unknown",
                reason="validation_failed",
            )

        # Check if can activate (offline check)
        can_activate, reason = self.activation_manager.can_activate(license_data)
        if not can_activate:
            raise LicenseError(
                f"Cannot activate license: {reason}",
                license_type=license_data.get("license_type", "unknown"),
                reason="activation_failed",
            )

        # Activate license (offline)
        activated_license = self.activation_manager.activate_license(license_data)

        # Add activation metadata
        activated_license["activation_date"] = datetime.now().isoformat()
        activated_license["validation_mode"] = validation_mode
        activated_license["license_key"] = license_key

        # Save to disk
        self._save_license(activated_license)

        return self.get_license_status()

    def deactivate_license(self) -> dict:
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

        # Remove license file
        if self.license_file.exists():
            self.license_file.unlink()

        self._current_license = None

        return self.get_license_status()

    def get_license_status(self) -> dict:
        """Get current license status.

        Returns:
            Dictionary with license information:
            - license_type: "trial" | "paid" | "none"
            - activated: Whether a paid license is activated
            - trial_status: Trial information (if applicable)
            - email: License holder email (if paid)
            - expiry_date: License expiry (if applicable)

        Example:
            >>> manager = LicenseManager()
            >>> status = manager.get_license_status()
            >>> if status['license_type'] == 'trial':
            ...     print(f"Trial: {status['trial_status']['remaining']} left")
        """
        if self._current_license:
            # Paid license active
            return {
                "license_type": "paid",
                "activated": True,
                "email": self._current_license.get("email"),
                "activation_date": self._current_license.get("activation_date"),
                "expiry_date": self._current_license.get("expiry_date"),
                "features": self._current_license.get("features", ["all"]),
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

        if status["license_type"] == "paid":
            # Paid license - check features list
            features = status.get("features", ["all"])
            return "all" in features or feature in features

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

        if status["license_type"] == "paid":
            # Paid license - no limit
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
        file_size_bytes = kwargs.get("file_size_bytes", 0)

        if status["license_type"] == "trial":
            # Record for trial tracking
            self.trial_manager.record_conversion(
                converter_name=converter_name,
                input_file=input_file,
                output_file=kwargs.get("output_file"),
                file_size_bytes=file_size_bytes,
                success=kwargs.get("success", True),
            )
        elif status["license_type"] == "paid" and self.supabase_backend:
            # Log usage to Supabase for paid licenses
            try:
                if self._current_license and "license_key" in self._current_license:
                    # Get license ID from stored data
                    license_id = self._current_license.get("id")
                    if license_id:
                        self.supabase_backend.log_usage(
                            license_id=license_id,
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
