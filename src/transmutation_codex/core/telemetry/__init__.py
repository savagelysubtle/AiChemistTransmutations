"""Telemetry system for AiChemist Transmutation Codex.

This package provides anonymous usage tracking with user consent,
event collection, and analytics integration.

Public API:
    - init_telemetry() - Initialize the telemetry system
    - track_event(event_name, properties) - Track a custom event
    - track_conversion(converter, success, **metadata) - Track conversion attempts
    - track_error(error_type, error_message) - Track errors
    - get_consent_status() - Get current consent status
    - request_consent() - Request telemetry consent from user
    - grant_consent() - Grant telemetry consent
    - revoke_consent() - Revoke telemetry consent
    - flush_events() - Manually flush pending events

Example usage:
    >>> from transmutation_codex.core.telemetry import init_telemetry, track_conversion
    >>>
    >>> # Initialize at app startup
    >>> init_telemetry()
    >>>
    >>> # Track a conversion
    >>> track_conversion("pdf2md", success=True, file_size_mb=2.5, duration_seconds=3.2)
"""

from .collector import TelemetryCollector, get_collector
from .consent import ConsentManager, get_consent_manager
from .events import EventType, TelemetryEvent

# Initialize managers (singletons)
_collector: TelemetryCollector | None = None
_consent_manager: ConsentManager | None = None


def init_telemetry(config: dict | None = None) -> None:
    """Initialize the telemetry system.

    Should be called once at application startup.

    Args:
        config: Optional configuration dictionary. If None, loads from ConfigManager.

    Example:
        >>> init_telemetry()
    """
    global _collector, _consent_manager

    _consent_manager = get_consent_manager()
    _collector = get_collector(config)

    # Start collector if consent is granted
    if _consent_manager.has_consent():
        _collector.start()


def track_event(event_name: str, properties: dict | None = None) -> None:
    """Track a custom event.

    Args:
        event_name: Name of the event (e.g., "button_clicked", "feature_used")
        properties: Optional properties dictionary (must not contain PII)

    Example:
        >>> track_event("pdf_merge_initiated", {"file_count": 3})
    """
    if _collector and _consent_manager and _consent_manager.has_consent():
        event = TelemetryEvent(
            event_type=EventType.CUSTOM,
            event_name=event_name,
            properties=properties or {},
        )
        _collector.track(event)


def track_conversion(
    converter_name: str,
    success: bool,
    **metadata,
) -> None:
    """Track a conversion attempt.

    Args:
        converter_name: Name of converter (e.g., "pdf2md", "md2pdf")
        success: Whether the conversion succeeded
        **metadata: Additional metadata (file_size_mb, duration_seconds, etc.)

    Example:
        >>> track_conversion("pdf2md", True, file_size_mb=2.5, duration_seconds=3.2)
    """
    if _collector and _consent_manager and _consent_manager.has_consent():
        event = TelemetryEvent(
            event_type=EventType.CONVERSION,
            event_name="conversion_attempt",
            properties={
                "converter": converter_name,
                "success": success,
                **metadata,
            },
        )
        _collector.track(event)


def track_error(error_type: str, error_message: str | None = None, **context) -> None:
    """Track an error occurrence.

    Args:
        error_type: Type of error (e.g., "ValidationError", "ConversionError")
        error_message: Optional error message (should not contain PII)
        **context: Additional error context

    Example:
        >>> track_error("FileNotFoundError", "Input file missing", converter="pdf2md")
    """
    if _collector and _consent_manager and _consent_manager.has_consent():
        event = TelemetryEvent(
            event_type=EventType.ERROR,
            event_name="error_occurred",
            properties={
                "error_type": error_type,
                "error_message": error_message,
                **context,
            },
        )
        _collector.track(event)


def track_feature_usage(feature_name: str, **properties) -> None:
    """Track feature usage.

    Args:
        feature_name: Name of the feature used
        **properties: Additional properties

    Example:
        >>> track_feature_usage("batch_conversion", file_count=10)
    """
    if _collector and _consent_manager and _consent_manager.has_consent():
        event = TelemetryEvent(
            event_type=EventType.FEATURE_USAGE,
            event_name=feature_name,
            properties=properties,
        )
        _collector.track(event)


def get_consent_status() -> dict:
    """Get current consent status.

    Returns:
        Dictionary with consent information:
        - has_consent: bool - Whether consent is granted
        - consent_date: str | None - When consent was granted
        - can_request: bool - Whether we can request consent

    Example:
        >>> status = get_consent_status()
        >>> if status["has_consent"]:
        ...     print("Telemetry enabled")
    """
    if _consent_manager:
        return {
            "has_consent": _consent_manager.has_consent(),
            "consent_date": _consent_manager.get_consent_date(),
            "can_request": _consent_manager.can_request_consent(),
        }
    return {"has_consent": False, "consent_date": None, "can_request": True}


def request_consent() -> bool:
    """Request telemetry consent from user.

    This should trigger a UI dialog. The actual granting of consent
    should be done via grant_consent() when the user accepts.

    Returns:
        bool: True if consent can be requested

    Example:
        >>> if request_consent():
        ...     # Show consent dialog to user
        ...     pass
    """
    if _consent_manager:
        return _consent_manager.can_request_consent()
    return False


def grant_consent() -> None:
    """Grant telemetry consent.

    Should be called when user explicitly accepts telemetry.

    Example:
        >>> grant_consent()
        >>> # Start tracking events
    """
    if _consent_manager:
        _consent_manager.grant_consent()
        if _collector:
            _collector.start()


def revoke_consent() -> None:
    """Revoke telemetry consent.

    Should be called when user opts out of telemetry.

    Example:
        >>> revoke_consent()
        >>> # Stop tracking events
    """
    if _consent_manager:
        _consent_manager.revoke_consent()
        if _collector:
            _collector.stop()
            _collector.clear_events()


def flush_events() -> None:
    """Manually flush pending events to backend.

    Normally events are batched and flushed automatically.

    Example:
        >>> flush_events()  # Send all pending events now
    """
    if _collector:
        _collector.flush()


def shutdown_telemetry() -> None:
    """Shutdown the telemetry system.

    Should be called at application shutdown.

    Example:
        >>> shutdown_telemetry()
    """
    if _collector:
        _collector.stop()
        _collector.flush()


__all__ = [
    # Initialization
    "init_telemetry",
    "shutdown_telemetry",
    # Event tracking
    "track_event",
    "track_conversion",
    "track_error",
    "track_feature_usage",
    # Consent management
    "get_consent_status",
    "request_consent",
    "grant_consent",
    "revoke_consent",
    # Manual control
    "flush_events",
    # Classes (for advanced usage)
    "TelemetryCollector",
    "ConsentManager",
    "TelemetryEvent",
    "EventType",
]
