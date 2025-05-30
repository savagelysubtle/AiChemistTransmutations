"""Pytest configuration for MDtoPDF tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def example_md_path():
    """Path to an example markdown file."""
    return Path(__file__).parent / "examples" / "output_examples" / "example.md"


@pytest.fixture
def example_md_content(example_md_path):
    """Content of the example markdown file."""
    with open(example_md_path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def example_pdf_path():
    """Path to an example PDF file."""
    return Path(__file__).parent / "examples" / "output_examples" / "example.pdf"


@pytest.fixture
def output_pdf_path(temp_dir):
    """Path to a temporary output PDF file."""
    return temp_dir / "output.pdf"


@pytest.fixture
def output_html_path(temp_dir):
    """Path to a temporary output HTML file."""
    return temp_dir / "output.html"


@pytest.fixture
def output_md_path(temp_dir):
    """Path to a temporary output Markdown file."""
    return temp_dir / "output.md"
