#!/usr/bin/env python3
"""Script to generate API documentation for the MDtoPDF package.

This script uses sphinx-apidoc to generate reStructuredText files for the
MDtoPDF package API documentation.
"""

import os
import subprocess
import shutil
from pathlib import Path

# Directory configurations
DOCS_DIR = Path(__file__).parent.absolute()
SOURCE_DIR = DOCS_DIR / "source"
API_DIR = SOURCE_DIR / "api"
SRC_DIR = DOCS_DIR.parent / "src" / "mdtopdf"

def main():
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

    # Run sphinx-apidoc to generate .rst files
    print(f"Running sphinx-apidoc on {SRC_DIR}...")
    subprocess.run([
        "sphinx-apidoc",
        "-f",  # Force overwriting of existing files
        "-e",  # Put documentation for each module on its own page
        "-M",  # Put module documentation before submodule documentation
        "-o", str(API_DIR),  # Output directory
        str(SRC_DIR),  # Source code directory
    ], check=True)

    print("API documentation generation complete!")
    print(f"API documentation files created in: {API_DIR}")

    # Make sure the modules.rst file is included in the index toctree
    index_file = SOURCE_DIR / "index.rst"
    if index_file.exists():
        with open(index_file, "r") as f:
            content = f.read()

        if "api/modules" not in content:
            print("Warning: 'api/modules' not found in index.rst toctree.")
            print("Make sure to include it in your documentation structure.")

    print("\nNext steps:")
    print("1. Build the documentation: sphinx-build -b html docs/source docs/build/html")
    print("2. Check the generated documentation for any issues")

if __name__ == "__main__":
    main()