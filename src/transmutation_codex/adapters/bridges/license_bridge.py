#!/usr/bin/env python
"""License Bridge - CLI interface for license operations.

This script is called by the Electron main process to handle license operations.
It outputs JSON to stdout for easy parsing by JavaScript.

Can be run directly or via Python's -m flag.
"""

import json
import sys
import traceback
from pathlib import Path

# Fix for PyInstaller: Handle closed stderr gracefully
# PyInstaller sometimes closes stderr, so we detect this early
_stderr_available = True
if hasattr(sys, 'frozen') and sys.frozen:
    # Running as PyInstaller bundle - check if stderr is available
    try:
        sys.stderr.write('')
        sys.stderr.flush()
    except (ValueError, OSError, AttributeError):
        # stderr is closed or unavailable - we'll use stdout for everything
        _stderr_available = False
        # Create a dummy stderr that writes to stdout
        import io
        sys.stderr = io.StringIO()  # Dummy that discards output

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup logging to stderr so it doesn't interfere with JSON output
# But handle case where stderr might be closed (PyInstaller builds)
import logging

# Use the global stderr availability check
if _stderr_available:
    try:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[LICENSE_BRIDGE] %(levelname)s: %(message)s',
            stream=sys.stderr
        )
    except (ValueError, OSError):
        # Fallback to stdout if stderr fails
        logging.basicConfig(
            level=logging.DEBUG,
            format='[LICENSE_BRIDGE] %(levelname)s: %(message)s',
            stream=sys.stdout
        )
else:
    # If stderr is not available, use a null handler or stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format='[LICENSE_BRIDGE] %(levelname)s: %(message)s',
        stream=sys.stdout
    )

logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("LICENSE BRIDGE STARTED")
logger.info("=" * 80)
logger.info(f"Python version: {sys.version}")
logger.info(f"Script path: {__file__}")
logger.info(f"Project root: {project_root}")
logger.info(f"sys.path: {sys.path[:3]}...")  # First 3 entries
logger.info(f"Arguments: {sys.argv}")
logger.info(f"Argument count: {len(sys.argv)}")

# Check environment variables
import os
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
logger.info(f"SUPABASE_URL: {'***set***' if supabase_url else 'NOT SET'}")
logger.info(f"SUPABASE_ANON_KEY: {'***set***' if supabase_anon_key else 'NOT SET'}")
if not supabase_url or not supabase_anon_key:
    logger.warning("⚠ Supabase credentials not found - will use offline validation only")

try:
    from transmutation_codex.core.licensing import (
        activate_license_key,
        deactivate_current_license,
        get_full_license_status,
        get_trial_status,
    )
    logger.info("✓ Successfully imported licensing functions")
except ImportError as e:
    logger.error(f"✗ Failed to import licensing functions: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    output_json({"success": False, "error": f"Import error: {str(e)}"})
    sys.exit(1)


def output_json(data: dict):
    """Output JSON to stdout.

    This function MUST always succeed, even if logging fails.
    """
    json_str = json.dumps(data)

    # Try to log, but don't fail if logging fails
    try:
        logger.info(f"Outputting JSON: {json_str[:200]}..." if len(json_str) > 200 else f"Outputting JSON: {json_str}")
    except Exception:
        pass

    # Always output JSON to stdout, regardless of logging status
    try:
        print(json_str)
        sys.stdout.flush()
    except Exception as e:
        # If stdout also fails, try stderr as last resort
        try:
            sys.stderr.write(json_str + '\n')
            sys.stderr.flush()
        except Exception:
            # If both fail, we're in serious trouble - but at least we tried
            pass


def handle_get_status():
    """Get current license status."""
    logger.info("Handling get-status command")
    try:
        logger.info("Calling get_full_license_status()")
        status = get_full_license_status()
        logger.info(f"✓ Got status: {status}")
        output_json(status)
    except Exception as e:
        logger.error(f"✗ Error getting status: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        output_json({"error": str(e), "license_type": "trial"})


def handle_activate(license_key: str):
    """Activate a license key."""
    try:
        logger.info("Handling activate command")
        logger.info(f"License key length: {len(license_key)}")
        logger.info(f"License key first 50 chars: {license_key[:50]}...")
        logger.info(f"License key last 20 chars: ...{license_key[-20:]}")
    except Exception:
        # If logging fails, continue anyway
        pass

    try:
        try:
            logger.info("Calling activate_license_key()")
        except Exception:
            pass

        status = activate_license_key(license_key)

        try:
            logger.info(f"✓ Activation successful: {status}")
        except Exception:
            pass

        output_json({"success": True, "status": status})
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        error_traceback = traceback.format_exc()

        # Try to log, but don't fail if logging fails
        try:
            logger.error(f"✗ Activation failed: {e}")
            logger.error(f"Exception type: {error_type}")
            logger.error(f"Traceback: {error_traceback}")
        except Exception:
            pass

        # Always output JSON error, even if logging fails
        output_json({"success": False, "error": error_msg})
        sys.exit(1)


def handle_deactivate():
    """Deactivate current license."""
    logger.info("Handling deactivate command")
    try:
        logger.info("Calling deactivate_current_license()")
        status = deactivate_current_license()
        logger.info(f"✓ Deactivation successful: {status}")
        output_json({"success": True, "status": status})
    except Exception as e:
        logger.error(f"✗ Deactivation failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        output_json({"success": False, "error": str(e)})
        sys.exit(1)


def handle_get_trial_status():
    """Get trial status."""
    logger.info("Handling get-trial-status command")
    try:
        logger.info("Calling get_trial_status()")
        status = get_trial_status()
        logger.info(f"✓ Got trial status: {status}")
        output_json(status)
    except Exception as e:
        logger.error(f"✗ Error getting trial status: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        output_json({"error": str(e), "status": "error"})


def main():
    """Main entry point."""
    try:
        logger.info("-" * 80)
        logger.info("MAIN FUNCTION ENTRY")
    except Exception:
        pass  # Continue even if logging fails

    if len(sys.argv) < 2:
        try:
            logger.error("✗ No command specified")
        except Exception:
            pass
        output_json({"error": "No command specified"})
        sys.exit(1)

    command = sys.argv[1]
    try:
        logger.info(f"Command: {command}")
    except Exception:
        pass

    try:
        if command == "get-status":
            handle_get_status()
        elif command == "activate":
            if len(sys.argv) < 3:
                try:
                    logger.error("✗ No license key provided")
                except Exception:
                    pass
                output_json({"error": "No license key provided"})
                sys.exit(1)
            handle_activate(sys.argv[2])
        elif command == "deactivate":
            handle_deactivate()
        elif command == "get-trial-status":
            handle_get_trial_status()
        else:
            try:
                logger.error(f"✗ Unknown command: {command}")
            except Exception:
                pass
            output_json({"error": f"Unknown command: {command}"})
            sys.exit(1)

        try:
            logger.info("=" * 80)
            logger.info("LICENSE BRIDGE COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
        except Exception:
            pass
    except Exception as e:
        # Catch any unexpected errors and output JSON before exiting
        error_msg = str(e)
        try:
            logger.critical(f"FATAL ERROR: {e}")
            logger.critical(f"Traceback: {traceback.format_exc()}")
        except Exception:
            pass
        output_json({"success": False, "error": f"Fatal error: {error_msg}"})
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"FATAL ERROR: {e}")
        logger.critical(f"Traceback: {traceback.format_exc()}")
        output_json({"success": False, "error": f"Fatal error: {str(e)}"})
        sys.exit(1)
