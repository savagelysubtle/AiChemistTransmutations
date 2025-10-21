#!/usr/bin/env python3
"""Startup script for AiChemist Transmutation Codex."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

from transmutation_codex.adapters.cli.dependency_status import check_dependency_status
from transmutation_codex.adapters.cli.gui_launcher import launch_gui
from transmutation_codex.core import get_log_manager


def auto_activate_dev_license():
    """Auto-activate developer license ONLY if explicitly in dev mode."""
    try:
        # Strict check: Must have DEV_MODE=true explicitly set
        # This prevents auto-activation in production builds
        is_dev = os.getenv("DEV_MODE", "").lower() == "true"

        if not is_dev:
            return  # Silent skip in production

        print("\n🔑 Auto-activating developer license...")

        from transmutation_codex.core.licensing import (
            activate_license_key,
            get_license_manager,
        )
        from transmutation_codex.core.licensing.supabase_backend import SupabaseBackend

        # Check if already activated
        manager = get_license_manager()
        if manager._current_license:
            current_email = manager._current_license.get("email")
            if current_email == "dev@aichemist.local":
                print("✅ Developer license already active")
                return

        # Get license key from Supabase
        backend = SupabaseBackend()

        if not backend.is_online_available():
            print("⚠️  Supabase not available. Skipping auto-activation.")
            return

        result = (
            backend.client.table("licenses")
            .select("*")
            .eq("email", "dev@aichemist.local")
            .execute()
        )

        if not result.data or len(result.data) == 0:
            print("⚠️  Developer license not found in Supabase.")
            return

        license_key = result.data[0]["license_key"]

        # Activate the license
        status = activate_license_key(license_key)

        if status.get("activated"):
            print("✅ Developer license activated")
            print("   Email: dev@aichemist.local")
            print(f"   Type: {status.get('license_type', 'Perpetual')}")
        else:
            error_msg = status.get("error", "Unknown error")
            print(f"⚠️  Failed to activate: {error_msg}")

    except Exception as e:
        print(f"⚠️  Auto-activation failed: {e}")


def main():
    """Main startup function."""
    logger = get_log_manager().get_converter_logger("startup")

    print("🚀 AiChemist Transmutation Codex")
    print("=" * 40)

    # Auto-activate dev license if in dev mode
    auto_activate_dev_license()

    # Check dependencies first
    print("\n🔍 Checking dependencies...")
    try:
        check_dependency_status("text")
        print("✅ All dependencies available")
    except SystemExit as e:
        if e.code == 1:
            print("\n⚠️  Some dependencies are missing.")
            print("The application may have limited functionality.")
            print("Continuing with available features...")
        else:
            raise

    # Launch GUI
    print("\n🚀 Launching GUI...")
    try:
        launch_gui()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"❌ Startup error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
