"""PyInstaller runtime hook to configure bundled external dependencies.

This hook runs when the frozen application starts and adds bundled
external tools (Tesseract, Ghostscript, Pandoc) to the system PATH.
"""

import os
import sys
from pathlib import Path


def add_bundled_tools_to_path():
    """Add bundled external tools to system PATH.

    Detects if running as frozen (PyInstaller) and adds the bundled
    resources directory to PATH so external tools can be found.
    """
    # Check if running as a PyInstaller bundle
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)

        # Add bundled tools to PATH
        tools_to_add = [
            bundle_dir / "resources" / "tesseract",
            bundle_dir / "resources" / "ghostscript" / "bin",
            bundle_dir / "resources" / "pandoc",
        ]

        # Get current PATH
        current_path = os.environ.get("PATH", "")
        path_entries = current_path.split(os.pathsep) if current_path else []

        # Add tool directories that exist
        for tool_dir in tools_to_add:
            if tool_dir.exists():
                tool_dir_str = str(tool_dir)
                if tool_dir_str not in path_entries:
                    path_entries.insert(0, tool_dir_str)

        # Update PATH environment variable
        os.environ["PATH"] = os.pathsep.join(path_entries)

        # Also set TESSDATA_PREFIX for Tesseract
        tessdata_dir = bundle_dir / "resources" / "tesseract" / "tessdata"
        if tessdata_dir.exists():
            os.environ["TESSDATA_PREFIX"] = str(tessdata_dir.parent)


# Execute on import
add_bundled_tools_to_path()

