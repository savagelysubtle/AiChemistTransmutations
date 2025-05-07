"""Tests for the PDF converter module."""

import os

import pytest  # type: ignore

from mdtopdf.converters.markdown_to_pdf import convert_md_to_pdf


def test_convert_md_to_pdf(example_md_path, output_pdf_path):
    """Test that convert_md_to_pdf creates a PDF file."""
    # Convert markdown to PDF
    result_path = convert_md_to_pdf(example_md_path, output_pdf_path)

    # Check that the output file exists
    assert os.path.exists(result_path)
    assert result_path.suffix == ".pdf"
    assert result_path == output_pdf_path


def test_convert_md_to_pdf_auto_output(example_md_path, temp_dir):
    """Test that convert_md_to_pdf creates a PDF file with auto-generated filename."""
    # Get the working directory
    os.chdir(temp_dir)

    # Convert markdown to PDF without specifying output
    result_path = convert_md_to_pdf(example_md_path)

    # The result should have the same name as the input but with .pdf extension
    expected_path = temp_dir / f"{example_md_path.stem}.pdf"

    # Check that the output file exists
    assert os.path.exists(result_path)
    assert result_path.suffix == ".pdf"
    assert result_path == expected_path


def test_convert_md_to_pdf_non_existent_file():
    """Test that convert_md_to_pdf raises an error for non-existent files."""
    with pytest.raises(FileNotFoundError):
        convert_md_to_pdf("non_existent_file.md")
