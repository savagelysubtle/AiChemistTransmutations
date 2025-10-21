#!/usr/bin/env python3
"""Quick test to verify the environment."""

import sys
from pathlib import Path

def test_imports():
    """Test that we can import the core modules."""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from transmutation_codex.core import get_registry, get_log_manager, get_progress_tracker
        print("✅ Core imports successful")
        
        # Test registry
        registry = get_registry()
        print(f"✅ Registry loaded: {len(registry._plugins)} plugin groups")
        
        # Test log manager
        log_manager = get_log_manager()
        print("✅ Log manager loaded")
        
        # Test progress tracker
        progress_tracker = get_progress_tracker()
        print("✅ Progress tracker loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_registry():
    """Test the plugin registry."""
    print("\n🧪 Testing plugin registry...")
    
    try:
        from transmutation_codex.core import get_registry
        
        registry = get_registry()
        
        # Test PDF to MD converters
        pdf_to_md_plugins = registry.get_plugins_for_conversion("pdf", "md")
        print(f"✅ PDF to MD converters: {len(pdf_to_md_plugins)}")
        
        for plugin in pdf_to_md_plugins:
            print(f"  - {plugin.name} (priority: {plugin.priority})")
        
        # Test MD to PDF converters
        md_to_pdf_plugins = registry.get_plugins_for_conversion("md", "pdf")
        print(f"✅ MD to PDF converters: {len(md_to_pdf_plugins)}")
        
        for plugin in md_to_pdf_plugins:
            print(f"  - {plugin.name} (priority: {plugin.priority})")
        
        # Test best converter selection
        best_pdf_to_md = registry.get_converter("pdf", "md")
        if best_pdf_to_md:
            print(f"✅ Best PDF to MD converter: {best_pdf_to_md.name} (priority: {best_pdf_to_md.priority})")
        
        return True
        
    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        return False

def test_progress_system():
    """Test the progress tracking system."""
    print("\n🧪 Testing progress system...")
    
    try:
        from transmutation_codex.core import start_operation, update_progress, complete_operation, get_operation
        
        # Start operation
        operation_id = start_operation("test_conversion", message="Test conversion", total_steps=3)
        print(f"✅ Started operation: {operation_id}")
        
        # Update progress
        update_progress(operation_id, 1, "Step 1")
        update_progress(operation_id, 2, "Step 2")
        print("✅ Progress updates successful")
        
        # Complete operation
        complete_operation(operation_id, success=True)
        print("✅ Operation completed")
        
        # Get operation details
        operation = get_operation(operation_id)
        if operation:
            print(f"✅ Operation details: {operation.operation_name}, status: {operation.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Progress test failed: {e}")
        return False

def test_event_system():
    """Test the event system."""
    print("\n🧪 Testing event system...")
    
    try:
        from transmutation_codex.core import Event, EventTypes, publish, subscribe, unsubscribe
        
        # Test event creation
        event = Event("test_event", source="test_source")
        print("✅ Event creation successful")
        
        # Test event types
        print(f"✅ Event types available: {len(list(EventTypes))}")
        
        # Test subscription (mock)
        handler_called = False
        def test_handler(event):
            nonlocal handler_called
            handler_called = True
        
        subscribe_id = subscribe("test_event", test_handler)
        print("✅ Event subscription successful")
        
        # Test publishing
        publish(event)
        print("✅ Event publishing successful")
        
        # Cleanup
        unsubscribe(subscribe_id)
        print("✅ Event unsubscription successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Event test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Transmutation Codex Quick Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_registry,
        test_progress_system,
        test_event_system
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All quick tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)