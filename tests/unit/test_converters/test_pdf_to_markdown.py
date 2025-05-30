"""Tests for the Markdown converter module (PDF to Markdown)."""

import os

import pytest  # type: ignore
from mdtopdf.converters.pdf_to_markdown import convert_pdf_to_md


def test_convert_pdf_to_md(example_pdf_path, output_md_path):
    """Test that convert_pdf_to_md creates a Markdown file."""
    # Convert PDF to Markdown
    result_path = convert_pdf_to_md(example_pdf_path, output_md_path)

    # Check that the output file exists
    assert os.path.exists(result_path)
    assert result_path.suffix == ".md"
    assert result_path == output_md_path


def test_convert_pdf_to_md_auto_output(example_pdf_path, temp_dir):
    """Test that convert_pdf_to_md creates a Markdown file with auto-generated filename."""
    # Get the working directory
    os.chdir(temp_dir)

    # Convert PDF to Markdown without specifying output
    result_path = convert_pdf_to_md(example_pdf_path)

    # The result should have the same name as the input but with .md extension
    expected_path = temp_dir / f"{example_pdf_path.stem}.md"

    # Check that the output file exists
    assert os.path.exists(result_path)
    assert result_path.suffix == ".md"
    assert result_path == expected_path


def test_convert_pdf_to_md_non_existent_file():
    """Test that convert_pdf_to_md raises an error for non-existent files."""
    with pytest.raises(FileNotFoundError):
        convert_pdf_to_md("non_existent_file.pdf")


def test_convert_pdf_to_md_non_pdf_file(example_md_path):
    """Test that convert_pdf_to_md raises an error for non-PDF files."""
    with pytest.raises(ValueError):
        convert_pdf_to_md(example_md_path)
