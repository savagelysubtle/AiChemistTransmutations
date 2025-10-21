"""Auto-activate developer license on startup.

This script retrieves the developer license from Supabase and activates it
automatically when running in development mode.
"""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

# Load environment variables
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)


def get_dev_license_key():
    """Retrieve the developer license key from Supabase."""
    try:
        from transmutation_codex.core.licensing.supabase_backend import SupabaseBackend

        backend = SupabaseBackend()

        # Check if Supabase is available
        if not backend.is_online_available():
            print("Warning: Supabase not available. Skipping auto-activation.")
            return None

        # Query for dev license
        result = (
            backend.client.table("licenses")
            .select("*")
            .eq("email", "dev@aichemist.local")
            .execute()
        )

        if result.data and len(result.data) > 0:
            license_data = result.data[0]
            return license_data["license_key"]
        else:
            print("Warning: Developer license not found in Supabase.")
            return None

    except Exception as e:
        print(f"Warning: Failed to retrieve dev license: {e}")
        return None


def activate_dev_license():
    """Activate the developer license."""
    try:
        from transmutation_codex.core.licensing import (
            activate_license_key,
            get_license_manager,
        )

        # Check if already activated
        manager = get_license_manager()
        if manager._current_license:
            current_email = manager._current_license.get("email")
            if current_email == "dev@aichemist.local":
                print("✓ Developer license already activated")
                return True

        # Get license key from Supabase
        license_key = get_dev_license_key()
        if not license_key:
            print("Warning: Could not retrieve dev license key")
            return False

        # Activate the license
        status = activate_license_key(license_key)

        if status.get("activated"):
            print("✓ Developer license activated successfully")
            print("  Email: dev@aichemist.local")
            print(f"  Type: {status.get('license_type', 'Perpetual')}")
            return True
        else:
            error_msg = status.get("error", "Unknown error")
            print(f"✗ Failed to activate dev license: {error_msg}")
            return False

    except Exception as e:
        print(f"✗ Error activating dev license: {e}")
        return False


def main():
    """Main entry point."""
    print("\n=== Auto-Activating Developer License ===")

    # Check if we're in development mode
    is_dev = os.getenv("NODE_ENV") == "development" or os.getenv("DEV_MODE") == "true"

    if not is_dev:
        # Also check if .env has SUPABASE_URL (indicates dev setup)
        is_dev = os.getenv("SUPABASE_URL") is not None

    if is_dev:
        activate_dev_license()
    else:
        print("Not in development mode. Skipping auto-activation.")

    print()


if __name__ == "__main__":
    main()
