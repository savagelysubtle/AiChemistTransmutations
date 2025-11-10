#!/usr/bin/env python
"""Standalone CLI entry point for license bridge.

This script can be called directly from PyInstaller bundles without
using the -m flag, avoiding the stderr closure issue.
"""

import sys
import os

# Ensure we can import from the package
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    # Add the bundle directory to path
    bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

# Import the license bridge module
try:
    from transmutation_codex.adapters.bridges.license_bridge import main
except ImportError as e:
    # Fallback: try to output error to stdout (stderr might be closed)
    print('{"success": false, "error": "Import error: ' + str(e) + '"}')
    sys.exit(1)

if __name__ == "__main__":
    # Call the main function from license_bridge
    try:
        main()
    except Exception as e:
        # Last resort error handling
        try:
            print('{"success": false, "error": "Fatal error: ' + str(e) + '"}')
        except Exception:
            pass
        sys.exit(1)




