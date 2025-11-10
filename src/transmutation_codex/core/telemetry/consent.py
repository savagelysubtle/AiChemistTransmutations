"""Telemetry consent management.

This module handles user consent for telemetry tracking, storing consent
status persistently and ensuring compliance with privacy regulations.
"""

import json
from datetime import UTC, datetime
from pathlib import Path


class ConsentManager:
    """Manages user consent for telemetry tracking."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_dir: Path | None = None):
        """Initialize the consent manager.

        Args:
            data_dir: Directory for storing consent data.
                     Defaults to platform-specific AppData directory.
        """
        if getattr(self, "_initialized", False):
            return

        if data_dir is None:
            data_dir = self._get_app_data_dir()

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Consent file path
        self.consent_file = self.data_dir / "telemetry_consent.json"

        # Load consent status
        self._consent_data = self._load_consent()

        self._initialized = True

    @staticmethod
    def _get_app_data_dir() -> Path:
        """Get platform-specific application data directory."""
        import os
        import platform

        system = platform.system()

        if system == "Windows":
            appdata = os.getenv("APPDATA")
            if appdata:
                return Path(appdata) / "AiChemist"
            return Path.home() / "AppData" / "Roaming" / "AiChemist"

        elif system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "AiChemist"

        else:
            xdg_data_home = os.getenv("XDG_DATA_HOME")
            if xdg_data_home:
                return Path(xdg_data_home) / "aichemist"
            return Path.home() / ".local" / "share" / "aichemist"

    def _load_consent(self) -> dict:
        """Load consent data from disk."""
        if not self.consent_file.exists():
            return {
                "consent_given": False,
                "consent_date": None,
                "consent_version": "1.0",
                "last_requested": None,
                "request_count": 0,
            }

        try:
            with open(self.consent_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "consent_given": False,
                "consent_date": None,
                "consent_version": "1.0",
                "last_requested": None,
                "request_count": 0,
            }

    def _save_consent(self):
        """Save consent data to disk."""
        with open(self.consent_file, "w") as f:
            json.dump(self._consent_data, f, indent=2)

    def has_consent(self) -> bool:
        """Check if user has granted telemetry consent.

        Returns:
            bool: True if consent is granted
        """
        return self._consent_data.get("consent_given", False)

    def grant_consent(self) -> None:
        """Grant telemetry consent.

        Should be called when user explicitly accepts telemetry.
        """
        self._consent_data["consent_given"] = True
        self._consent_data["consent_date"] = datetime.now(UTC).isoformat()
        self._consent_data["consent_version"] = "1.0"
        self._save_consent()

    def revoke_consent(self) -> None:
        """Revoke telemetry consent.

        Should be called when user opts out of telemetry.
        """
        self._consent_data["consent_given"] = False
        self._consent_data["consent_date"] = None
        self._save_consent()

    def get_consent_date(self) -> str | None:
        """Get the date when consent was granted.

        Returns:
            str | None: ISO format date string, or None if consent not granted
        """
        return self._consent_data.get("consent_date")

    def can_request_consent(self) -> bool:
        """Check if we can request consent from the user.

        Implements a rate limit to avoid pestering users.
        - Don't ask again if already granted
        - Don't ask more than once per day
        - Don't ask more than 3 times total

        Returns:
            bool: True if we can request consent
        """
        # Already granted - don't ask again
        if self.has_consent():
            return False

        # Check request count
        request_count = self._consent_data.get("request_count", 0)
        if request_count >= 3:
            # Asked 3 times already - stop asking
            return False

        # Check last request date
        last_requested = self._consent_data.get("last_requested")
        if last_requested:
            last_request_date = datetime.fromisoformat(last_requested)
            time_since_last_request = datetime.now(UTC) - last_request_date
            # Don't ask more than once per day
            if time_since_last_request.total_seconds() < 86400:  # 24 hours
                return False

        return True

    def record_consent_request(self) -> None:
        """Record that consent was requested from the user.

        Updates the request count and last requested timestamp.
        """
        self._consent_data["last_requested"] = datetime.now(UTC).isoformat()
        self._consent_data["request_count"] = (
            self._consent_data.get("request_count", 0) + 1
        )
        self._save_consent()

    def get_consent_status(self) -> dict:
        """Get comprehensive consent status information.

        Returns:
            dict: Consent status with keys:
                - has_consent: bool
                - consent_date: str | None
                - can_request: bool
                - request_count: int
                - last_requested: str | None
        """
        return {
            "has_consent": self.has_consent(),
            "consent_date": self.get_consent_date(),
            "can_request": self.can_request_consent(),
            "request_count": self._consent_data.get("request_count", 0),
            "last_requested": self._consent_data.get("last_requested"),
        }

    def reset(self) -> None:
        """Reset consent data (for testing purposes only)."""
        self._consent_data = {
            "consent_given": False,
            "consent_date": None,
            "consent_version": "1.0",
            "last_requested": None,
            "request_count": 0,
        }
        self._save_consent()


# Singleton accessor
_consent_manager: ConsentManager | None = None


def get_consent_manager(data_dir: Path | None = None) -> ConsentManager:
    """Get the singleton ConsentManager instance.

    Args:
        data_dir: Optional data directory (only used on first call)

    Returns:
        ConsentManager: The singleton instance
    """
    global _consent_manager
    if _consent_manager is None:
        _consent_manager = ConsentManager(data_dir)
    return _consent_manager
