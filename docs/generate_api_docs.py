#!/usr/bin/env python3
"""Script to generate API documentation for the Aichemist Transmutation Codex.

This script uses sphinx-apidoc to scan the Python source code and generate
reStructuredText (.rst) files. These .rst files are then used by sphinx-build
(typically run by build_docs.py or manually) to create the final HTML
documentation.

Key functions of sphinx-apidoc used here:
- It explores the package structure in the `SRC_DIR`.
- Creates .rst files for each module and package it finds.
- Generates a `modules.rst` file, which is a table of contents for all modules.
"""

import subprocess
from pathlib import Path

# --- Configuration Section ---
# Path to the directory containing this script (docs/)
DOCS_DIR = Path(__file__).parent.absolute()
# Path to the Sphinx source directory (docs/source/)
SOURCE_DIR = DOCS_DIR / "source"
# Path where sphinx-apidoc will output the generated .rst files (docs/source/api/)
API_DIR = SOURCE_DIR / "api"
# Path to the actual Python source code of the project (src/aichemist_transmutation_codex/)
SRC_DIR = DOCS_DIR.parent / "src" / "aichemist_transmutation_codex"
# --- End Configuration Section ---


def main():
    """Main function to orchestrate the API documentation generation."""
    print("Starting API documentation generation (sphinx-apidoc)...")

    # Ensure the target directory for API .rst files exists.
    # If it exists, clean out old .rst files to prevent stale documentation.
    if not API_DIR.exists():
        print(f"Creating API output directory: {API_DIR}")
        API_DIR.mkdir(parents=True)
    else:
        print(f"Cleaning existing API documentation files from: {API_DIR}")
        # Remove any .rst files from the API_DIR to ensure a fresh build.
        for file in API_DIR.glob("*.rst"):
            print(f"  Deleting old file: {file.name}")
            file.unlink()

    # Construct the sphinx-apidoc command.
    # For more details on sphinx-apidoc options, see:
    # https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html
    cmd = [
        "sphinx-apidoc",
        "-f",  # --force: Overwrite existing files without asking.
        "-e",  # --separate: Put documentation for each module on its own page.
        "-M",  # --module-first: Put module documentation before submodule documentation.
        "-o",
        str(API_DIR),  # Output directory for the generated .rst files.
        str(SRC_DIR),  # Path to the Python package to document.
        # You can add paths to exclude here if needed, for example:
        # str(SRC_DIR / 'tests'), # Exclude the tests directory
    ]

    print(f"Running sphinx-apidoc with command: {' '.join(cmd)}")
    print(f"  Source code directory: {SRC_DIR}")
    print(f"  Output API .rst directory: {API_DIR}")

    # Execute the sphinx-apidoc command.
    try:
        # `check=True` will raise a CalledProcessError if sphinx-apidoc fails.
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("sphinx-apidoc executed successfully!")
    except subprocess.CalledProcessError as e:
        print("Error during sphinx-apidoc execution:")
        print(f"  Return code: {e.returncode}")
        print(f"  Stdout:\n{e.stdout}")
        print(f"  Stderr:\n{e.stderr}")
        # Optionally, re-raise or exit here if preferred
        # return 1 # Indicate failure

    print(f"API documentation .rst files generated in: {API_DIR}")

    # Reminder to include the generated API docs in the main Sphinx toctree.
    # sphinx-apidoc creates a `modules.rst` file (or similar, depending on options)
    # which serves as the main entry point for the API documentation.
    # This file needs to be included in a `toctree` directive in your main
    # `index.rst` or another relevant .rst file in `docs/source/`.
    index_file = SOURCE_DIR / "index.rst"
    api_modules_file_relative = API_DIR.relative_to(SOURCE_DIR) / "modules.rst"

    if index_file.exists():
        with open(index_file, encoding="utf-8") as f:
            content = f.read()

        # Check if the typical entry point for API docs (`api/modules`) is in a toctree.
        # Note: The actual file might be different if -T (no-toc) or other options are used.
        if str(api_modules_file_relative).replace("\\", "/") not in content:
            print("\n--- IMPORTANT REMINDER ---")
            print(
                f"Warning: '{api_modules_file_relative}' does not seem to be included in a toctree in '{index_file}'."
            )
            print(
                "Please ensure you add it to a .. toctree:: directive in your main documentation files"
            )
            print(
                " (e.g., in docs/source/index.rst) so that the API documentation is reachable."
            )
            print("Example for index.rst:")
            print("  .. toctree::")
            print("     :maxdepth: 2")
            print("     :caption: API Reference")
            print("")
            print(f"     {api_modules_file_relative}")
            print("--------------------------")
    else:
        print(
            f"Warning: Main index file '{index_file}' not found. Cannot check for API toctree inclusion."
        )

    print("\nAPI documentation generation process complete.")
    print(
        "Next steps typically involve running sphinx-build to generate HTML (or other formats)."
    )
    print("This is usually handled by a script like 'build_docs.py' or by running:")
    print(f'  sphinx-build -b html "{SOURCE_DIR}" "{DOCS_DIR / "build" / "html"}"')


if __name__ == "__main__":
    main()
