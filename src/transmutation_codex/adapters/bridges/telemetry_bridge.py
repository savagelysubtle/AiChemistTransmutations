"""Telemetry bridge for Electron GUI integration.

This script provides a command-line interface for the telemetry system,
allowing the Electron frontend to interact with Python telemetry functions.

Usage:
    python telemetry_bridge.py <command> [args]

Commands:
    get-consent-status  - Get current telemetry consent status
    grant-consent       - Grant telemetry consent
    revoke-consent      - Revoke telemetry consent
"""

import json
import sys

from transmutation_codex.core import telemetry


def get_consent_status() -> dict:
    """Get telemetry consent status.

    Returns:
        dict: Consent status information
    """
    try:
        status = telemetry.get_consent_status()
        return {
            "success": True,
            "has_consent": status.get("has_consent", False),
            "consent_date": status.get("consent_date"),
            "can_request": status.get("can_request", True),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def grant_consent() -> dict:
    """Grant telemetry consent.

    Returns:
        dict: Operation result
    """
    try:
        telemetry.grant_consent()
        return {"success": True, "message": "Telemetry consent granted"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def revoke_consent() -> dict:
    """Revoke telemetry consent.

    Returns:
        dict: Operation result
    """
    try:
        telemetry.revoke_consent()
        return {"success": True, "message": "Telemetry consent revoked"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main entry point for telemetry bridge CLI."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No command provided"}, indent=2))
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "get-consent-status":
            result = get_consent_status()
        elif command == "grant-consent":
            result = grant_consent()
        elif command == "revoke-consent":
            result = revoke_consent()
        else:
            result = {
                "success": False,
                "error": f"Unknown command: {command}",
            }

        print(json.dumps(result, indent=2))
        sys.exit(0 if result.get("success", False) else 1)

    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
