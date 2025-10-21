"""Hardware fingerprinting and license activation.

This module generates unique machine identifiers for license binding
and handles license activation/deactivation.
"""

import hashlib
import platform
import uuid
from pathlib import Path


class MachineFingerprint:
    """Generate unique machine fingerprints for license binding."""

    @staticmethod
    def get_machine_id() -> str:
        """Generate a unique machine identifier.

        Uses a combination of:
        - MAC address (primary network adapter)
        - Machine UUID (from SMBIOS)
        - Hostname

        Returns:
            Unique machine identifier (SHA256 hash)

        Example:
            >>> fingerprint = MachineFingerprint()
            >>> machine_id = fingerprint.get_machine_id()
            >>> print(f"Machine ID: {machine_id}")
        """
        # Get MAC address (most reliable identifier)
        mac = uuid.getnode()
        mac_str = f"{mac:012x}"

        # Get hostname
        hostname = platform.node()

        # Try to get machine UUID (Windows/Linux)
        machine_uuid = ""
        try:
            if platform.system() == "Windows":
                import subprocess

                result = subprocess.run(
                    ["wmic", "csproduct", "get", "UUID"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if len(lines) >= 2:
                        machine_uuid = lines[1].strip()
            elif platform.system() == "Linux":
                machine_id_path = Path("/etc/machine-id")
                if machine_id_path.exists():
                    machine_uuid = machine_id_path.read_text().strip()
        except Exception:
            # Fall back to just MAC + hostname if UUID unavailable
            pass

        # Combine identifiers
        combined = f"{mac_str}:{hostname}:{machine_uuid}"

        # Hash to create consistent identifier
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @staticmethod
    def validate_machine_id(stored_machine_id: str, current_machine_id: str) -> bool:
        """Validate that current machine matches stored machine ID.

        Args:
            stored_machine_id: Machine ID from license activation
            current_machine_id: Current machine's ID

        Returns:
            True if machine IDs match
        """
        return stored_machine_id == current_machine_id


class ActivationManager:
    """Manage license activation and deactivation."""

    def __init__(self, license_file_path: Path):
        """Initialize activation manager.

        Args:
            license_file_path: Path to license storage file
        """
        self.license_file_path = license_file_path
        self.fingerprint = MachineFingerprint()

    def can_activate(self, license_data: dict) -> tuple[bool, str]:
        """Check if license can be activated on this machine.

        Args:
            license_data: License data from validated key

        Returns:
            Tuple of (can_activate, reason)
        """
        # Check if license is already activated
        activated_machine = license_data.get("machine_id")
        if not activated_machine:
            # Not yet activated - can activate
            return True, "License not yet activated"

        # Check if activated on this machine
        current_machine = self.fingerprint.get_machine_id()
        if activated_machine == current_machine:
            return True, "License already activated on this machine"

        # Activated on different machine
        max_activations = license_data.get("max_activations", 1)
        if max_activations > 1:
            # Multi-device license (future enhancement)
            return False, "Multi-device licenses not yet supported"

        return False, "License already activated on another machine"

    def activate_license(self, license_data: dict) -> dict:
        """Activate license on current machine.

        Args:
            license_data: License data from validated key

        Returns:
            Updated license data with machine binding
        """
        machine_id = self.fingerprint.get_machine_id()

        # Add machine binding
        license_data["machine_id"] = machine_id
        license_data["activated"] = True

        return license_data

    def deactivate_license(self, license_data: dict) -> dict:
        """Deactivate license from current machine.

        Args:
            license_data: Current license data

        Returns:
            Updated license data without machine binding
        """
        # Remove machine binding
        if "machine_id" in license_data:
            del license_data["machine_id"]
        license_data["activated"] = False

        return license_data

    def is_activated_on_this_machine(self, license_data: dict) -> bool:
        """Check if license is activated on this machine.

        Args:
            license_data: License data to check

        Returns:
            True if activated on current machine
        """
        activated_machine = license_data.get("machine_id")
        if not activated_machine:
            return False

        current_machine = self.fingerprint.get_machine_id()
        return activated_machine == current_machine
