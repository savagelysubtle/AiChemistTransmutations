"""PyInstaller runtime hook for AiChemist Transmutation Codex

This hook automatically configures PATH to include bundled executables
(Tesseract, Ghostscript, and Pandoc) when the application starts.

This ensures OCR, PDF processing, and DOCX conversion work immediately without manual configuration.
"""

import os
import sys
from pathlib import Path


def setup_bundled_executables():
    """Add bundled Tesseract, Ghostscript, and Pandoc to PATH at runtime.

    This function runs automatically when the frozen application starts.
    It detects the bundled executables and adds them to PATH so they
    can be found by subprocess calls.

    Cross-platform compatible:
    - Windows: tesseract.exe, gswin64c.exe, pandoc.exe
    - Linux/macOS: tesseract, gs, pandoc
    """
    try:
        # Determine if running as frozen executable or script
        if getattr(sys, "frozen", False):
            # Running as compiled executable (PyInstaller)
            base_dir = Path(sys._MEIPASS)
            is_frozen = True
        else:
            # Running as script (development) - shouldn't happen but just in case
            base_dir = Path(__file__).parent.parent
            is_frozen = False

        # List of bundled executable directories to add to PATH
        bundled_dirs = []

        # Add Tesseract directory
        tesseract_dir = base_dir / "resources" / "tesseract"
        if tesseract_dir.exists():
            bundled_dirs.append(str(tesseract_dir))
            print(f"[Runtime Hook] Found bundled Tesseract at: {tesseract_dir}")

        # Add Ghostscript directory
        ghostscript_dir = base_dir / "resources" / "ghostscript"
        if ghostscript_dir.exists():
            bundled_dirs.append(str(ghostscript_dir))
            print(f"[Runtime Hook] Found bundled Ghostscript at: {ghostscript_dir}")

        # Add Pandoc directory
        pandoc_dir = base_dir / "resources" / "pandoc"
        if pandoc_dir.exists():
            bundled_dirs.append(str(pandoc_dir))
            print(f"[Runtime Hook] Found bundled Pandoc at: {pandoc_dir}")

        # Add directories to PATH (prepend so they take priority)
        if bundled_dirs:
            current_path = os.environ.get("PATH", "")
            new_path_entries = os.pathsep.join(bundled_dirs)

            if current_path:
                os.environ["PATH"] = new_path_entries + os.pathsep + current_path
            else:
                os.environ["PATH"] = new_path_entries

            print(f"[Runtime Hook] Added {len(bundled_dirs)} director(ies) to PATH")

            # Verify executables are accessible
            if is_frozen:
                _verify_executables()
        else:
            print("[Runtime Hook] No bundled executables found (development mode?)")

    except Exception as e:
        # Don't crash the app if PATH setup fails
        print(f"[Runtime Hook] Warning: Failed to configure PATH: {e}")


def _verify_executables():
    """Verify that bundled executables are accessible."""
    import shutil

    executables_to_check = []

    # Platform-specific executable names
    if sys.platform == "win32":
        executables_to_check = ["tesseract.exe", "gswin64c.exe", "pandoc.exe"]
    else:
        executables_to_check = ["tesseract", "gs", "pandoc"]

    for exe in executables_to_check:
        if shutil.which(exe):
            print(f"[Runtime Hook] ✓ {exe} is accessible in PATH")
        else:
            print(f"[Runtime Hook] ✗ {exe} not found in PATH")


# Run the setup automatically when this module is imported
setup_bundled_executables()
