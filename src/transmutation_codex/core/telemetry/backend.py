"""Telemetry backend integration with Supabase.

This module sends telemetry events to the Supabase analytics backend.
"""

import os

from .events import TelemetryEvent

# Optional Supabase integration
try:
    from supabase import Client, create_client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None  # type: ignore


class TelemetryBackend:
    """Backend for sending telemetry events to Supabase."""

    def __init__(self):
        """Initialize the telemetry backend.

        Connects to Supabase using environment variables:
        - SUPABASE_URL: Supabase project URL
        - SUPABASE_ANON_KEY: Supabase anonymous/public key
        """
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "Supabase client not available. Install with: pip install supabase"
            )

        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY environment variables required"
            )

        self.client: Client = create_client(self.url, self.key)
        self.table_name = "telemetry_events"

    def send_events(self, events: list[TelemetryEvent]) -> bool:
        """Send a batch of events to Supabase.

        Args:
            events: List of TelemetryEvent objects to send

        Returns:
            bool: True if events were sent successfully

        Raises:
            Exception: If sending fails
        """
        if not events:
            return True

        # Convert events to dictionaries
        event_data = [event.to_dict() for event in events]

        # Send to Supabase
        try:
            response = self.client.table(self.table_name).insert(event_data).execute()
            return True
        except Exception as e:
            print(f"Failed to send telemetry events: {e}")
            raise

    def send_event(self, event: TelemetryEvent) -> bool:
        """Send a single event to Supabase.

        Args:
            event: TelemetryEvent to send

        Returns:
            bool: True if event was sent successfully
        """
        return self.send_events([event])

    def test_connection(self) -> bool:
        """Test the connection to Supabase.

        Returns:
            bool: True if connection is working
        """
        try:
            # Try to query the table (limit 0 to avoid loading data)
            self.client.table(self.table_name).select("*").limit(0).execute()
            return True
        except Exception as e:
            print(f"Supabase connection test failed: {e}")
            return False


def is_backend_configured() -> bool:
    """Check if telemetry backend is properly configured.

    Returns:
        bool: True if Supabase credentials are available
    """
    return bool(
        SUPABASE_AVAILABLE
        and os.getenv("SUPABASE_URL")
        and os.getenv("SUPABASE_ANON_KEY")
    )


def create_backend() -> TelemetryBackend | None:
    """Create a telemetry backend if configured.

    Returns:
        TelemetryBackend | None: Backend instance or None if not configured
    """
    if not is_backend_configured():
        return None

    try:
        return TelemetryBackend()
    except Exception as e:
        print(f"Failed to create telemetry backend: {e}")
        return None
