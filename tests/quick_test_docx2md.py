"""Quick test script to verify docx2md converter registration."""

import sys
from pathlib import Path

# Add src to path if running directly
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print("Testing DOCX to Markdown converter registration...")

    try:
        # Import the plugins module to trigger registration

        # Get the registry
        from transmutation_codex.core import get_registry

        registry = get_registry()

        # Check available conversions
        available = registry.get_available_conversions()
        print(f"\nAvailable conversions: {available}")

        # Check if docx2md is registered
        docx_converters = available.get("docx", [])
        print(f"\nDOCX converters: {docx_converters}")

        if "md" in docx_converters:
            print("\n✓ SUCCESS: docx2md converter is registered!")

            # Get the actual converter
            plugin_info = registry.get_converter("docx", "md")
            print(f"  Plugin info: {plugin_info}")

            sys.exit(0)
        else:
            print("\n✗ FAILED: docx2md converter not found in registry")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
