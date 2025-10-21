#!/usr/bin/env python
"""Test script to verify plugin registry integration."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(backend_dir))

# Import and trigger plugin registration
import transmutation_codex.plugins  # noqa: F401
from transmutation_codex.core import get_registry

def test_plugin_registry():
    """Test that the plugin registry is working."""
    print("=" * 60)
    print("PLUGIN REGISTRY TEST")
    print("=" * 60)

    # Get the registry
    registry = get_registry()

    # List all available conversions
    conversions = registry.get_available_conversions()
    print(f"\n✓ Found {len(conversions)} conversion types:")
    for source_format, target_formats in sorted(conversions.items()):
        for target_format in sorted(target_formats):
            conversion_key = f"{source_format}2{target_format}"
            plugins = registry.get_plugins_for_conversion(source_format, target_format)
            print(f"  • {conversion_key:15} - {len(plugins)} plugin(s)")

            # Show plugin details
            for plugin in plugins:
                print(f"    ├─ {plugin.name} (v{plugin.version}, priority={plugin.priority})")
                print(f"    └─ {plugin.description}")

    # Test specific conversions
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC CONVERTERS")
    print("=" * 60)

    test_cases = [
        ("md", "pdf"),
        ("pdf", "md"),
        ("txt", "pdf"),
    ]

    for source, target in test_cases:
        print(f"\n→ Testing {source}2{target}:")
        plugin = registry.get_converter(source, target)
        if plugin:
            print(f"  ✓ Found: {plugin.name}")
            print(f"    Description: {plugin.description}")
            print(f"    Version: {plugin.version}")
            print(f"    Priority: {plugin.priority}")
            print(f"    Supports batch: {plugin.supports_batch}")
            print(f"    Supports options: {plugin.supports_options}")
        else:
            print(f"  ✗ No converter found")

    # Test conversion support check
    print("\n" + "=" * 60)
    print("SUPPORTED FORMATS")
    print("=" * 60)
    input_formats = registry.get_supported_input_formats()
    output_formats = registry.get_supported_output_formats()

    print(f"\n✓ Input formats:  {', '.join(sorted(input_formats))}")
    print(f"✓ Output formats: {', '.join(sorted(output_formats))}")

    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_plugins = registry.list_plugins()
    print(f"✓ Total plugins registered: {len(all_plugins)}")
    print(f"✓ Conversion types available: {len(conversions)}")
    print(f"✓ Input formats supported: {len(input_formats)}")
    print(f"✓ Output formats supported: {len(output_formats)}")

    print("\n✅ Plugin registry test PASSED!\n")
    return True

if __name__ == "__main__":
    try:
        test_plugin_registry()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Plugin registry test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
