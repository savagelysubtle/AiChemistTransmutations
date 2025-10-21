"""Centralized version management for AiChemist Transmutation Codex.

This module provides a single source of truth for version information
across the entire application including Python backend, Electron GUI,
installers, and documentation.
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__build__ = "2025.01"
__release_date__ = "2025-01-15"

# Build metadata
BUILD_TYPE = "production"  # "development" | "production" | "beta"
BUILD_CHANNEL = "stable"  # "stable" | "beta" | "dev"

# Application metadata
APP_NAME = "AiChemist Transmutation Codex"
APP_ID = "com.aichemist.transmutationcodex"
COMPANY_NAME = "AiChemist"
COPYRIGHT = f"© 2024-2025 {COMPANY_NAME}. All rights reserved."

# Update information
UPDATE_CHECK_URL = (
    "https://api.github.com/repos/yourorg/transmutation-codex/releases/latest"
)
RELEASE_NOTES_URL = "https://github.com/yourorg/transmutation-codex/releases"

# License information
LICENSE_TYPE = "Proprietary"
LICENSE_URL = "https://yourcompany.com/license"


def get_version_string(include_build: bool = False) -> str:
    """Get formatted version string.

    Args:
        include_build: Include build number in version string

    Returns:
        Version string (e.g., "1.0.0" or "1.0.0+2025.01")
    """
    if include_build:
        return f"{__version__}+{__build__}"
    return __version__


def get_full_version_info() -> dict:
    """Get complete version information.

    Returns:
        Dictionary with all version metadata
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build": __build__,
        "build_type": BUILD_TYPE,
        "build_channel": BUILD_CHANNEL,
        "release_date": __release_date__,
        "app_name": APP_NAME,
        "app_id": APP_ID,
        "company": COMPANY_NAME,
        "copyright": COPYRIGHT,
    }


# For backwards compatibility
VERSION = __version__
BUILD = __build__
