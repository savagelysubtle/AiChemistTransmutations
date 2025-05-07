"""End-to-end tests for the MDtoPDF package."""

import os
import subprocess
import sys


def test_cli_end_to_end(example_md_path, temp_dir):
    """Test the CLI converts a file end-to-end."""
    # Define output file
    output_path = temp_dir / "output.pdf"

    # Run the CLI using subprocess
    cmd = [
        sys.executable,
        "-m",
        "mdtopdf",
        str(example_md_path),
        "--output",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check the command ran successfully
    assert result.returncode == 0, f"Command failed: {result.stderr}"

    # Check the output file exists
    assert os.path.exists(output_path)
    assert output_path.stat().st_size > 0, "Output file is empty"


def test_cli_html_output(example_md_path, temp_dir):
    """Test the CLI converts a file to HTML."""
    # Define output file
    output_path = temp_dir / "output.html"

    # Run the CLI using subprocess
    cmd = [
        sys.executable,
        "-m",
        "mdtopdf",
        str(example_md_path),
        "--output",
        str(output_path),
        "--format",
        "html",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check the command ran successfully
    assert result.returncode == 0, f"Command failed: {result.stderr}"

    # Check the output file exists
    assert os.path.exists(output_path)
    assert output_path.stat().st_size > 0, "Output file is empty"

    # Read the HTML file and check it contains the expected content
    with open(output_path, encoding="utf-8") as f:
        content = f.read()

    # Check that the HTML includes key markdown elements
    assert "<html" in content
    assert "<body" in content
    assert "</html>" in content
