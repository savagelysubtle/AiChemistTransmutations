#!/usr/bin/env python
"""License Bridge - CLI interface for license operations.

This script is called by the Electron main process to handle license operations.
It outputs JSON to stdout for easy parsing by JavaScript.
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from transmutation_codex.core.licensing import (
    activate_license_key,
    deactivate_current_license,
    get_full_license_status,
    get_trial_status,
)


def output_json(data: dict):
    """Output JSON to stdout."""
    print(json.dumps(data))
    sys.stdout.flush()


def handle_get_status():
    """Get current license status."""
    try:
        status = get_full_license_status()
        output_json(status)
    except Exception as e:
        output_json({"error": str(e), "license_type": "trial"})


def handle_activate(license_key: str):
    """Activate a license key."""
    try:
        status = activate_license_key(license_key)
        output_json({"success": True, "status": status})
    except Exception as e:
        output_json({"success": False, "error": str(e)})
        sys.exit(1)


def handle_deactivate():
    """Deactivate current license."""
    try:
        status = deactivate_current_license()
        output_json({"success": True, "status": status})
    except Exception as e:
        output_json({"success": False, "error": str(e)})
        sys.exit(1)


def handle_get_trial_status():
    """Get trial status."""
    try:
        status = get_trial_status()
        output_json(status)
    except Exception as e:
        output_json({"error": str(e), "status": "error"})


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        output_json({"error": "No command specified"})
        sys.exit(1)

    command = sys.argv[1]

    if command == "get-status":
        handle_get_status()
    elif command == "activate":
        if len(sys.argv) < 3:
            output_json({"error": "No license key provided"})
            sys.exit(1)
        handle_activate(sys.argv[2])
    elif command == "deactivate":
        handle_deactivate()
    elif command == "get-trial-status":
        handle_get_trial_status()
    else:
        output_json({"error": f"Unknown command: {command}"})
        sys.exit(1)


if __name__ == "__main__":
    main()
