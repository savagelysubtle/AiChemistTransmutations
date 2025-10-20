"""Tests for the event system."""

from unittest.mock import Mock

from transmutation_codex.core import (
    ConversionEvent,
    ErrorEvent,
    Event,
    EventBus,
    EventHandler,
    EventPriority,
    EventTypes,
    ProgressEvent,
    emit,
    get_event_bus,
    publish,
    subscribe,
    unsubscribe,
)


class TestEventSystem:
    """Test the event system."""

    def test_event_creation(self):
        """Test basic event creation."""
        event = Event("test_event")

        assert event.event_type == "test_event"
        assert event.timestamp > 0
        assert event.source is None
        assert event.data == {}
        assert event.cancellable is True
        assert event.cancelled is False

    def test_event_with_data(self):
        """Test event creation with data."""
        data = {"key": "value", "number": 42}
        event = Event("test_event", source="test_source", data=data)

        assert event.event_type == "test_event"
        assert event.source == "test_source"
        assert event.data == data

    def test_event_cancellation(self):
        """Test event cancellation."""
        event = Event("test_event")

        # Test cancellation
        event.cancel()
        assert event.cancelled is True
        assert event.is_cancelled() is True

        # Test non-cancellable event
        non_cancellable = Event("test_event", cancellable=False)
        non_cancellable.cancel()
        assert non_cancellable.cancelled is False

    def test_event_data_methods(self):
        """Test event data methods."""
        event = Event("test_event")

        # Test get_data
        assert event.get_data("key") is None
        assert event.get_data("key", "default") == "default"

        # Test set_data
        event.set_data("key", "value")
        assert event.get_data("key") == "value"

    def test_conversion_event(self):
        """Test ConversionEvent creation."""
        event = ConversionEvent(
            event_type=EventTypes.CONVERSION_STARTED,
            source="pdf2md",
            input_file="test.pdf",
            output_file="test.md",
            conversion_type="pdf2md",
            plugin_name="pdf_to_markdown",
        )

        assert event.event_type == EventTypes.CONVERSION_STARTED
        assert event.source == "pdf2md"
        assert event.input_file == "test.pdf"
        assert event.output_file == "test.md"
        assert event.conversion_type == "pdf2md"
        assert event.plugin_name == "pdf_to_markdown"

        # Test data population
        assert event.data["input_file"] == "test.pdf"
        assert event.data["output_file"] == "test.md"
        assert event.data["conversion_type"] == "pdf2md"
        assert event.data["plugin_name"] == "pdf_to_markdown"

    def test_progress_event(self):
        """Test ProgressEvent creation."""
        event = ProgressEvent(
            event_type=EventTypes.PROGRESS_UPDATED,
            operation_id="test_op",
            current_step=5,
            total_steps=10,
            progress_percentage=50.0,
        )

        assert event.event_type == EventTypes.PROGRESS_UPDATED
        assert event.operation_id == "test_op"
        assert event.current_step == 5
        assert event.total_steps == 10
        assert event.progress_percentage == 50.0

        # Test data population
        assert event.data["operation_id"] == "test_op"
        assert event.data["current_step"] == 5
        assert event.data["total_steps"] == 10
        assert event.data["progress_percentage"] == 50.0

    def test_error_event(self):
        """Test ErrorEvent creation."""
        event = ErrorEvent(
            event_type=EventTypes.CONVERSION_FAILED,
            source="pdf2md",
            error_message="Test error",
            exception_type="ConversionError",  # Fixed: exception_type, not error_type
        )

        assert event.event_type == EventTypes.CONVERSION_FAILED
        assert event.error_message == "Test error"
        assert event.exception_type == "ConversionError"

    def test_event_bus_subscription(self):
        """Test event bus subscription."""
        bus = EventBus()
        handler = Mock()

        # Subscribe to event
        subscribe_id = bus.subscribe("test_event", handler)

        assert subscribe_id is not None
        assert len(bus._handlers["test_event"]) == 1

        # Unsubscribe
        bus.unsubscribe(subscribe_id)
        assert len(bus._handlers["test_event"]) == 0

    def test_event_bus_priority(self):
        """Test event handler priorities."""
        bus = EventBus()
        handler1 = Mock()
        handler2 = Mock()
        handler3 = Mock()

        # Subscribe with different priorities
        bus.subscribe("test_event", handler1, priority=EventPriority.LOW)
        bus.subscribe("test_event", handler2, priority=EventPriority.HIGH)
        bus.subscribe("test_event", handler3, priority=EventPriority.NORMAL)

        # Publish event
        event = Event("test_event")
        bus.publish(event)

        # Verify handlers were called in priority order
        calls = [call[0][0] for call in handler1.call_args_list]
        calls.extend([call[0][0] for call in handler2.call_args_list])
        calls.extend([call[0][0] for call in handler3.call_args_list])

        # HIGH priority should be called first
        assert calls[0] == event

    def test_event_bus_publishing(self):
        """Test event publishing."""
        bus = EventBus()
        handler = Mock()

        # Subscribe
        bus.subscribe("test_event", handler)

        # Publish event
        event = Event("test_event")
        bus.publish(event)

        # Verify handler was called
        handler.assert_called_once_with(event)

    def test_event_bus_cancellation(self):
        """Test event cancellation during handling."""
        bus = EventBus()

        def cancel_handler(event):
            event.cancel()

        def normal_handler(event):
            # This should not be called if event is cancelled
            pass

        # Subscribe handlers
        bus.subscribe("test_event", cancel_handler, priority=EventPriority.HIGH)
        bus.subscribe("test_event", normal_handler, priority=EventPriority.LOW)

        # Publish event
        event = Event("test_event")
        bus.publish(event)

        # Verify event was cancelled
        assert event.cancelled is True

    def test_global_event_functions(self):
        """Test global event functions."""
        handler = Mock()

        # Subscribe using global function
        subscribe_id = subscribe("test_event", handler)

        # Publish using global function
        event = Event("test_event")
        publish(event)

        # Verify handler was called
        handler.assert_called_once_with(event)

        # Unsubscribe using global function
        unsubscribe(subscribe_id)

    def test_emit_function(self):
        """Test emit function."""
        handler = Mock()

        # Subscribe
        subscribe("test_event", handler)

        # Emit event
        emit("test_event", source="test_source", data={"key": "value"})

        # Verify handler was called
        handler.assert_called_once()
        event = handler.call_args[0][0]
        assert event.event_type == "test_event"
        assert event.source == "test_source"
        assert event.data["key"] == "value"

    def test_event_bus_singleton(self):
        """Test event bus singleton."""
        bus1 = get_event_bus()
        bus2 = get_event_bus()

        assert bus1 is bus2

    def test_event_handler_class(self):
        """Test EventHandler class."""

        class TestHandler(EventHandler):
            def __init__(self):
                self.events = []

            def handle(self, event):
                self.events.append(event)

        handler = TestHandler()
        bus = EventBus()

        # Subscribe handler
        bus.subscribe("test_event", handler)

        # Publish event
        event = Event("test_event")
        bus.publish(event)

        # Verify handler received event
        assert len(handler.events) == 1
        assert handler.events[0] == event

    def test_event_types_enum(self):
        """Test EventTypes enum values."""
        # Verify expected event type values
        assert EventTypes.CONVERSION_STARTED == "conversion.started"
        assert EventTypes.CONVERSION_COMPLETED == "conversion.completed"
        assert EventTypes.PROGRESS_UPDATED == "progress.updated"
        assert EventTypes.CONVERSION_FAILED == "conversion.failed"

    def test_event_priority_enum(self):
        """Test EventPriority enum."""
        assert EventPriority.LOWEST.value == 0
        assert EventPriority.LOW.value == 1
        assert EventPriority.NORMAL.value == 2
        assert EventPriority.HIGH.value == 3
        assert EventPriority.HIGHEST.value == 4

    def test_multiple_event_types(self):
        """Test handling multiple event types."""
        bus = EventBus()
        handler1 = Mock()
        handler2 = Mock()

        # Subscribe to different event types
        bus.subscribe("event_type_1", handler1)
        bus.subscribe("event_type_2", handler2)

        # Publish different events
        event1 = Event("event_type_1")
        event2 = Event("event_type_2")

        bus.publish(event1)
        bus.publish(event2)

        # Verify correct handlers were called
        handler1.assert_called_once_with(event1)
        handler2.assert_called_once_with(event2)

    def test_event_handler_exception(self):
        """Test event handler exception handling."""
        bus = EventBus()

        def error_handler(event):
            raise Exception("Handler error")

        def normal_handler(event):
            pass

        # Subscribe handlers
        bus.subscribe("test_event", error_handler)
        bus.subscribe("test_event", normal_handler)

        # Publish event - should not raise exception
        event = Event("test_event")
        bus.publish(event)

        # Both handlers should have been called
        # (exception in one handler shouldn't stop others)
