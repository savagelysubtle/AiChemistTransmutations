"""Telemetry event definitions and types.

This module defines the event structure and event types for telemetry tracking.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Types of telemetry events."""

    # Conversion events
    CONVERSION = "conversion"
    CONVERSION_STARTED = "conversion_started"
    CONVERSION_COMPLETED = "conversion_completed"
    CONVERSION_FAILED = "conversion_failed"

    # Feature usage
    FEATURE_USAGE = "feature_usage"
    BATCH_CONVERSION = "batch_conversion"
    PDF_MERGE = "pdf_merge"

    # Errors
    ERROR = "error"
    ERROR_VALIDATION = "error_validation"
    ERROR_CONVERSION = "error_conversion"
    ERROR_FILE_ACCESS = "error_file_access"

    # Performance
    PERFORMANCE = "performance"
    PERFORMANCE_SLOW = "performance_slow"

    # Licensing
    LICENSE_ACTIVATED = "license_activated"
    LICENSE_DEACTIVATED = "license_deactivated"
    TRIAL_STARTED = "trial_started"
    TRIAL_EXPIRED = "trial_expired"

    # Application lifecycle
    APP_STARTED = "app_started"
    APP_SHUTDOWN = "app_shutdown"

    # Custom events
    CUSTOM = "custom"


@dataclass
class TelemetryEvent:
    """Represents a single telemetry event."""

    event_type: EventType
    event_name: str
    properties: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str | None = None
    user_id: str | None = None  # Anonymous user ID (not PII)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization.

        Returns:
            dict: Event data as dictionary
        """
        data = asdict(self)
        # Convert enum to string value
        data["event_type"] = self.event_type.value
        return data

    def validate(self) -> bool:
        """Validate that the event contains no PII.

        Checks that properties don't contain common PII fields.

        Returns:
            bool: True if event is valid (no PII detected)

        Raises:
            ValueError: If PII is detected in event properties
        """
        pii_fields = {
            "email",
            "name",
            "first_name",
            "last_name",
            "phone",
            "address",
            "ip_address",
            "credit_card",
            "ssn",
            "password",
            "api_key",
            "token",
            "secret",
        }

        # Check for PII in property keys
        for key in self.properties.keys():
            if any(pii_field in key.lower() for pii_field in pii_fields):
                raise ValueError(
                    f"PII detected in event property: {key}. "
                    "Telemetry must not contain personally identifiable information."
                )

        # Check for PII in property values (only check string values)
        for key, value in self.properties.items():
            if isinstance(value, str):
                # Check if value looks like an email
                if "@" in value and "." in value.split("@")[-1]:
                    raise ValueError(
                        f"Possible email address detected in property '{key}': {value[:20]}..."
                    )

        return True

    @classmethod
    def create_conversion_event(
        cls,
        converter_name: str,
        success: bool,
        duration_seconds: float | None = None,
        file_size_mb: float | None = None,
        **extra_properties,
    ) -> "TelemetryEvent":
        """Create a conversion event.

        Args:
            converter_name: Name of the converter
            success: Whether conversion succeeded
            duration_seconds: How long the conversion took
            file_size_mb: Size of the input file
            **extra_properties: Additional properties

        Returns:
            TelemetryEvent: The created event
        """
        properties = {
            "converter": converter_name,
            "success": success,
        }

        if duration_seconds is not None:
            properties["duration_seconds"] = duration_seconds
        if file_size_mb is not None:
            properties["file_size_mb"] = file_size_mb

        properties.update(extra_properties)

        event_type = (
            EventType.CONVERSION_COMPLETED if success else EventType.CONVERSION_FAILED
        )

        return cls(
            event_type=event_type,
            event_name="conversion",
            properties=properties,
        )

    @classmethod
    def create_error_event(
        cls,
        error_type: str,
        error_message: str | None = None,
        **context,
    ) -> "TelemetryEvent":
        """Create an error event.

        Args:
            error_type: Type of error (exception class name)
            error_message: Error message (should not contain PII)
            **context: Additional error context

        Returns:
            TelemetryEvent: The created event
        """
        properties = {
            "error_type": error_type,
        }

        if error_message:
            # Truncate error message to prevent PII leakage
            properties["error_message"] = error_message[:200]

        properties.update(context)

        return cls(
            event_type=EventType.ERROR,
            event_name="error",
            properties=properties,
        )

    @classmethod
    def create_feature_usage_event(
        cls,
        feature_name: str,
        **properties,
    ) -> "TelemetryEvent":
        """Create a feature usage event.

        Args:
            feature_name: Name of the feature used
            **properties: Additional properties

        Returns:
            TelemetryEvent: The created event
        """
        return cls(
            event_type=EventType.FEATURE_USAGE,
            event_name=feature_name,
            properties=properties,
        )

    @classmethod
    def create_license_event(
        cls,
        action: str,
        license_type: str | None = None,
        **properties,
    ) -> "TelemetryEvent":
        """Create a license-related event.

        Args:
            action: Action performed (activated, deactivated, etc.)
            license_type: Type of license (trial, pro, enterprise)
            **properties: Additional properties

        Returns:
            TelemetryEvent: The created event
        """
        event_props = {}
        if license_type:
            event_props["license_type"] = license_type
        event_props.update(properties)

        event_type_map = {
            "activated": EventType.LICENSE_ACTIVATED,
            "deactivated": EventType.LICENSE_DEACTIVATED,
            "trial_started": EventType.TRIAL_STARTED,
            "trial_expired": EventType.TRIAL_EXPIRED,
        }

        return cls(
            event_type=event_type_map.get(action, EventType.CUSTOM),
            event_name=f"license_{action}",
            properties=event_props,
        )
