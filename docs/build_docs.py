#!/usr/bin/env python3
"""Build script for MDtoPDF Sphinx documentation.

This script automates the process of:
1. Generating API documentation using sphinx-apidoc
2. Building the HTML documentation using sphinx-build
"""

import os
import subprocess
import sys
from pathlib import Path

# Directory configurations
DOCS_DIR = Path(__file__).parent.absolute()
SOURCE_DIR = DOCS_DIR / "source"
BUILD_DIR = DOCS_DIR / "build"
API_DIR = SOURCE_DIR / "api"
SRC_DIR = DOCS_DIR.parent / "src" / "mdtopdf"

def generate_api_docs():
    """Generate API documentation using sphinx-apidoc."""
    print("Generating API documentation...")

    # Create API directory if it doesn't exist
    if not API_DIR.exists():
        API_DIR.mkdir(parents=True)
    else:
        # Clean existing API documentation
        print("Cleaning existing API documentation...")
        for file in API_DIR.glob("*.rst"):
            file.unlink()

    # Generate API documentation
    try:
        subprocess.run([
            "sphinx-apidoc",
            "-f",  # Force overwriting of existing files
            "-e",  # Put documentation for each module on its own page
            "-M",  # Put module documentation before submodule documentation
            "-o", str(API_DIR),  # Output directory
            str(SRC_DIR),  # Source code directory
        ], check=True)
        print("API documentation generation successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating API documentation: {e}")
        return False

    return True

def build_html_docs():
    """Build HTML documentation using sphinx-build."""
    print("Building HTML documentation...")

    # Create build directory if it doesn't exist
    if not BUILD_DIR.exists():
        BUILD_DIR.mkdir(parents=True)

    # Build HTML documentation
    try:
        subprocess.run([
            "sphinx-build",
            "-b", "html",  # Build HTML documentation
            "-d", str(BUILD_DIR / "doctrees"),  # Directory for cached doctrees
            str(SOURCE_DIR),  # Source directory
            str(BUILD_DIR / "html"),  # Output directory
        ], check=True)
        print("HTML documentation build successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error building HTML documentation: {e}")
        return False

    return True

def main():
    """Main function to run the documentation build process."""
    # Check if Sphinx is installed
    try:
        subprocess.run(["sphinx-build", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Sphinx is not installed or not in PATH.")
        print("Please install Sphinx: pip install sphinx sphinx-rtd-theme")
        return 1

    # Generate API documentation
    if not generate_api_docs():
        return 1

    # Build HTML documentation
    if not build_html_docs():
        return 1

    # Print success message with path to documentation
    html_index = BUILD_DIR / "html" / "index.html"
    print(f"\nDocumentation build complete!")
    print(f"Documentation is available at: {html_index.absolute()}")
    print(f"You can open it in your browser with: file://{html_index.absolute()}")

    return 0

if __name__ == "__main__":
    sys.exit(main())