"""Telemetry event collector and batcher.

This module collects telemetry events, batches them, and sends them
to the backend analytics service (Supabase).
"""

import threading
from collections import deque
from typing import Any

from .events import TelemetryEvent


class TelemetryCollector:
    """Collects and batches telemetry events for transmission."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config: dict | None = None):
        """Initialize the telemetry collector.

        Args:
            config: Optional configuration dictionary with keys:
                - batch_size: Number of events per batch (default: 50)
                - flush_interval: Seconds between auto-flushes (default: 300)
                - max_queue_size: Maximum events in queue (default: 1000)
                - enabled: Whether telemetry is enabled (default: False)
        """
        if getattr(self, "_initialized", False):
            return

        self.config = config or {}
        self.batch_size = self.config.get("batch_size", 50)
        self.flush_interval = self.config.get("flush_interval", 300)  # 5 minutes
        self.max_queue_size = self.config.get("max_queue_size", 1000)
        self.enabled = self.config.get("enabled", False)

        # Event queue
        self._events: deque[TelemetryEvent] = deque(maxlen=self.max_queue_size)
        self._lock = threading.Lock()

        # Background thread for auto-flushing
        self._flush_thread: threading.Thread | None = None
        self._stop_flag = threading.Event()
        self._running = False

        # Session ID (generated once per session)
        import uuid

        self.session_id = str(uuid.uuid4())

        # Initialize backend (lazy loaded)
        self._backend = None

        self._initialized = True

    def _get_backend(self):
        """Get or initialize the backend connection (lazy loaded)."""
        if self._backend is None:
            try:
                from .backend import TelemetryBackend

                self._backend = TelemetryBackend()
            except Exception as e:
                # Backend unavailable - events will be queued but not sent
                print(f"Telemetry backend unavailable: {e}")
                self._backend = None
        return self._backend

    def track(self, event: TelemetryEvent) -> None:
        """Track an event.

        Args:
            event: TelemetryEvent to track
        """
        if not self.enabled:
            return

        # Set session ID if not already set
        if event.session_id is None:
            event.session_id = self.session_id

        # Validate event (ensure no PII)
        try:
            event.validate()
        except ValueError as e:
            print(f"Event validation failed: {e}")
            return

        # Add to queue
        with self._lock:
            self._events.append(event)

            # Auto-flush if batch size reached
            if len(self._events) >= self.batch_size:
                self._flush_events()

    def _flush_events(self) -> None:
        """Flush events to backend (internal, assumes lock is held)."""
        if not self._events:
            return

        # Get all events
        events_to_send = list(self._events)
        self._events.clear()

        # Send to backend (release lock first to avoid blocking)
        backend = self._get_backend()
        if backend:
            try:
                backend.send_events(events_to_send)
            except Exception as e:
                print(f"Failed to send telemetry events: {e}")
                # Re-queue events (up to max queue size)
                with self._lock:
                    for event in reversed(events_to_send):
                        if len(self._events) < self.max_queue_size:
                            self._events.appendleft(event)
                        else:
                            break

    def flush(self) -> None:
        """Manually flush all pending events."""
        with self._lock:
            self._flush_events()

    def _flush_loop(self) -> None:
        """Background thread that periodically flushes events."""
        while not self._stop_flag.is_set():
            # Wait for flush interval or stop signal
            if self._stop_flag.wait(timeout=self.flush_interval):
                break  # Stop signal received

            # Flush events
            with self._lock:
                self._flush_events()

    def start(self) -> None:
        """Start the background flush thread."""
        if self._running:
            return

        self._stop_flag.clear()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
        self._running = True

    def stop(self) -> None:
        """Stop the background flush thread."""
        if not self._running:
            return

        self._stop_flag.set()
        if self._flush_thread:
            self._flush_thread.join(timeout=5)
        self._running = False

    def clear_events(self) -> None:
        """Clear all pending events (e.g., when consent is revoked)."""
        with self._lock:
            self._events.clear()

    def get_event_count(self) -> int:
        """Get the number of pending events.

        Returns:
            int: Number of events in the queue
        """
        with self._lock:
            return len(self._events)

    def get_stats(self) -> dict[str, Any]:
        """Get collector statistics.

        Returns:
            dict: Statistics including:
                - event_count: Number of pending events
                - running: Whether background thread is running
                - session_id: Current session ID
                - batch_size: Configured batch size
                - flush_interval: Configured flush interval
        """
        return {
            "event_count": self.get_event_count(),
            "running": self._running,
            "session_id": self.session_id,
            "batch_size": self.batch_size,
            "flush_interval": self.flush_interval,
            "enabled": self.enabled,
        }


# Singleton accessor
_collector: TelemetryCollector | None = None


def get_collector(config: dict | None = None) -> TelemetryCollector:
    """Get the singleton TelemetryCollector instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        TelemetryCollector: The singleton instance
    """
    global _collector
    if _collector is None:
        _collector = TelemetryCollector(config)
    return _collector
