"""Tests for the HTML converter module."""

import os

import pytest  # type: ignore
from mdtopdf.converters.markdown_to_html import convert_md_to_html


def test_convert_md_to_html(example_md_path, output_html_path):
    """Test that convert_md_to_html creates an HTML file."""
    # Convert markdown to HTML
    result_path = convert_md_to_html(example_md_path, output_html_path)

    # Check that the output file exists
    assert os.path.exists(result_path)
    assert result_path.suffix == ".html"
    assert result_path == output_html_path


def test_convert_md_to_html_auto_output(example_md_path, temp_dir):
    """Test that convert_md_to_html creates an HTML file with auto-generated filename."""
    # Get the working directory
    os.chdir(temp_dir)

    # Convert markdown to HTML without specifying output
    result_path = convert_md_to_html(example_md_path)

    # The result should have the same name as the input but with .html extension
    expected_path = temp_dir / f"{example_md_path.stem}.html"

    # Check that the output file exists
    assert os.path.exists(result_path)
    assert result_path.suffix == ".html"
    assert result_path == expected_path


def test_convert_md_to_html_non_existent_file():
    """Test that convert_md_to_html raises an error for non-existent files."""
    with pytest.raises(FileNotFoundError):
        convert_md_to_html("non_existent_file.md")


def test_convert_md_to_html_css(example_md_path, temp_dir):
    """Test that convert_md_to_html accepts custom CSS."""
    # Create a custom CSS file
    css_path = temp_dir / "custom.css"
    with open(css_path, "w") as f:
        f.write("body { background-color: red; }")

    # Convert markdown to HTML with custom CSS
    output_path = temp_dir / "output.html"
    result_path = convert_md_to_html(example_md_path, output_path)

    # Check that the output file exists
    assert os.path.exists(result_path)

    # Check that the CSS was included
    with open(result_path, encoding="utf-8") as f:
        content = f.read()

    # The CSS content should be in the file
    assert "background-color: red" in content
