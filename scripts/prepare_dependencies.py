"""Prepare external dependencies for PyInstaller bundling.

This script locates installed external dependencies (Tesseract, Ghostscript,
Pandoc) and copies them to the build/resources/ directory for inclusion in
the PyInstaller bundle.

Usage:
    python scripts/build/prepare_dependencies.py [--verbose]
"""

import argparse
import shutil
import sys
from pathlib import Path


class DependencyPreparer:
    """Prepares external dependencies for bundling."""

    def __init__(self, verbose: bool = False):
        """Initialize the dependency preparer.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.project_root = self._find_project_root()
        self.build_resources = self.project_root / "build" / "resources"
        self.build_resources.mkdir(parents=True, exist_ok=True)

    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / "pyproject.toml").exists():
                return parent
        return current.parent.parent.parent

    def log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def find_tesseract(self) -> tuple[bool, Path | None]:
        """Find Tesseract OCR installation.

        Returns:
            Tuple of (found, installation_path)
        """
        self.log("Searching for Tesseract OCR...")

        # Common installation paths
        tesseract_paths = [
            "C:\\Program Files\\Tesseract-OCR",
            "C:\\Program Files (x86)\\Tesseract-OCR",
            "/usr/share/tesseract-ocr",
            "/usr/local/share/tesseract-ocr",
            "/opt/homebrew/Cellar/tesseract",
        ]

        for path_str in tesseract_paths:
            path = Path(path_str)
            if path.exists():
                self.log(f"Found Tesseract at: {path}")
                return True, path

        # Check if in PATH
        tesseract_exe = shutil.which("tesseract")
        if tesseract_exe:
            # Get the installation directory
            tesseract_path = Path(tesseract_exe).parent.parent
            self.log(f"Found Tesseract in PATH: {tesseract_path}")
            return True, tesseract_path

        return False, None

    def find_ghostscript(self) -> tuple[bool, Path | None]:
        """Find Ghostscript installation.

        Returns:
            Tuple of (found, installation_path)
        """
        self.log("Searching for Ghostscript...")

        # Common installation paths
        gs_paths = [
            "C:\\Program Files\\gs",
            "C:\\Program Files (x86)\\gs",
            "/usr/share/ghostscript",
            "/usr/local/share/ghostscript",
            "/opt/homebrew/Cellar/ghostscript",
        ]

        for path_str in gs_paths:
            path = Path(path_str)
            if path.exists():
                # Find latest version on Windows
                if sys.platform == "win32":
                    version_dirs = list(path.glob("gs*"))
                    if version_dirs:
                        latest = max(version_dirs, key=lambda x: x.name)
                        self.log(f"Found Ghostscript at: {latest}")
                        return True, latest
                else:
                    self.log(f"Found Ghostscript at: {path}")
                    return True, path

        # Check if in PATH
        gs_exe = shutil.which("gs") or shutil.which("gswin64c")
        if gs_exe:
            # Get the installation directory
            gs_path = Path(gs_exe).parent.parent
            self.log(f"Found Ghostscript in PATH: {gs_path}")
            return True, gs_path

        return False, None

    def find_pandoc(self) -> tuple[bool, Path | None]:
        """Find Pandoc installation.

        Returns:
            Tuple of (found, installation_path)
        """
        self.log("Searching for Pandoc...")

        # Common installation paths
        pandoc_paths = [
            "C:\\Program Files\\Pandoc",
            "C:\\Program Files (x86)\\Pandoc",
            "/usr/bin",
            "/usr/local/bin",
            "/opt/homebrew/bin",
        ]

        for path_str in pandoc_paths:
            path = Path(path_str)
            pandoc_exe = (
                path / "pandoc.exe" if sys.platform == "win32" else path / "pandoc"
            )
            if pandoc_exe.exists():
                self.log(f"Found Pandoc at: {path}")
                return True, path

        # Check if in PATH
        pandoc_exe = shutil.which("pandoc")
        if pandoc_exe:
            # Get the installation directory
            pandoc_path = Path(pandoc_exe).parent
            self.log(f"Found Pandoc in PATH: {pandoc_path}")
            return True, pandoc_path

        return False, None

    def copy_tesseract(self, source_path: Path) -> bool:
        """Copy Tesseract to build directory.

        Args:
            source_path: Source installation path

        Returns:
            True if successful
        """
        dest_path = self.build_resources / "tesseract"

        try:
            # Clean destination
            if dest_path.exists():
                shutil.rmtree(dest_path)

            dest_path.mkdir(parents=True)

            # Copy executable
            if sys.platform == "win32":
                tesseract_exe = source_path / "tesseract.exe"
                if tesseract_exe.exists():
                    shutil.copy2(tesseract_exe, dest_path)
                    self.log(f"Copied: {tesseract_exe}")

            else:
                tesseract_exe = source_path / "bin" / "tesseract"
                if tesseract_exe.exists():
                    shutil.copy2(tesseract_exe, dest_path)
                    self.log(f"Copied: {tesseract_exe}")

            # Copy tessdata directory
            tessdata_source = source_path / "tessdata"
            if tessdata_source.exists():
                tessdata_dest = dest_path / "tessdata"
                shutil.copytree(tessdata_source, tessdata_dest)
                self.log(f"Copied tessdata: {tessdata_source}")
            else:
                # Try alternative locations
                for alt_path in [
                    "/usr/share/tesseract-ocr/4.00/tessdata",
                    "/usr/local/share/tessdata",
                ]:
                    alt_tessdata = Path(alt_path)
                    if alt_tessdata.exists():
                        tessdata_dest = dest_path / "tessdata"
                        shutil.copytree(alt_tessdata, tessdata_dest)
                        self.log(f"Copied tessdata from: {alt_tessdata}")
                        break

            print(f"✅ Tesseract copied to: {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to copy Tesseract: {e}")
            return False

    def copy_ghostscript(self, source_path: Path) -> bool:
        """Copy Ghostscript to build directory.

        Args:
            source_path: Source installation path

        Returns:
            True if successful
        """
        dest_path = self.build_resources / "ghostscript"

        try:
            # Clean destination
            if dest_path.exists():
                shutil.rmtree(dest_path)

            dest_path.mkdir(parents=True)

            # Copy bin directory
            bin_source = source_path / "bin"
            if bin_source.exists():
                bin_dest = dest_path / "bin"
                shutil.copytree(bin_source, bin_dest)
                self.log(f"Copied bin: {bin_source}")

            # Copy lib directory (fonts, resources)
            lib_source = source_path / "lib"
            if lib_source.exists():
                lib_dest = dest_path / "lib"
                shutil.copytree(lib_source, lib_dest)
                self.log(f"Copied lib: {lib_source}")

            print(f"✅ Ghostscript copied to: {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to copy Ghostscript: {e}")
            return False

    def copy_pandoc(self, source_path: Path) -> bool:
        """Copy Pandoc to build directory.

        Args:
            source_path: Source installation path

        Returns:
            True if successful
        """
        dest_path = self.build_resources / "pandoc"

        try:
            # Clean destination
            if dest_path.exists():
                shutil.rmtree(dest_path)

            dest_path.mkdir(parents=True)

            # Copy pandoc executable
            if sys.platform == "win32":
                pandoc_exe = source_path / "pandoc.exe"
            else:
                pandoc_exe = source_path / "pandoc"

            if pandoc_exe.exists():
                shutil.copy2(pandoc_exe, dest_path)
                self.log(f"Copied: {pandoc_exe}")
            else:
                print(f"⚠️  Pandoc executable not found at: {pandoc_exe}")
                return False

            print(f"✅ Pandoc copied to: {dest_path}")
            return True

        except Exception as e:
            print(f"❌ Failed to copy Pandoc: {e}")
            return False

    def prepare_all(self) -> bool:
        """Prepare all dependencies.

        Returns:
            True if all dependencies were prepared successfully
        """
        print("=" * 60)
        print("Preparing External Dependencies for Bundling")
        print("=" * 60)
        print()

        all_success = True

        # Tesseract
        found, path = self.find_tesseract()
        if found and path:
            if not self.copy_tesseract(path):
                all_success = False
        else:
            print("⚠️  Tesseract not found - OCR features will not be available")
            all_success = False

        print()

        # Ghostscript
        found, path = self.find_ghostscript()
        if found and path:
            if not self.copy_ghostscript(path):
                all_success = False
        else:
            print("⚠️  Ghostscript not found - PDF processing may be limited")
            all_success = False

        print()

        # Pandoc
        found, path = self.find_pandoc()
        if found and path:
            if not self.copy_pandoc(path):
                all_success = False
        else:
            print("⚠️  Pandoc not found - some conversions will not be available")
            all_success = False

        print()
        print("=" * 60)
        if all_success:
            print("✅ All dependencies prepared successfully!")
            print(f"📁 Build resources directory: {self.build_resources}")
        else:
            print("⚠️  Some dependencies could not be prepared")
            print("   Install missing dependencies and run this script again")
        print("=" * 60)

        return all_success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Prepare external dependencies for PyInstaller bundling"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()

    preparer = DependencyPreparer(verbose=args.verbose)
    success = preparer.prepare_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

