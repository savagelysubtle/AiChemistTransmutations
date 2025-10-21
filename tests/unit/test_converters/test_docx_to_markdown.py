"""Tests for DOCX to Markdown converter."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from transmutation_codex.plugins.docx.to_markdown import (
    convert_docx_to_markdown,
    get_pandoc_path,
)


class TestDOCXToMarkdownConverter:
    """Test the DOCX to Markdown converter."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_docx_file(self, tmp_path):
        """Create a mock DOCX file for testing."""
        docx_path = tmp_path / "test.docx"
        # Create a minimal DOCX file structure (just touch it for now)
        docx_path.touch()
        return docx_path

    @pytest.mark.unit
    def test_get_pandoc_path(self):
        """Test that pandoc path detection works or fails gracefully."""
        try:
            pandoc_path = get_pandoc_path()
            assert pandoc_path is not None
            assert len(pandoc_path) > 0
        except FileNotFoundError:
            # This is acceptable if pandoc is not installed
            pytest.skip("Pandoc not installed, skipping test")

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.docx.to_markdown.pypandoc.convert_file")
    @patch("transmutation_codex.plugins.docx.to_markdown.get_pandoc_path")
    def test_convert_docx_to_markdown_basic(
        self, mock_get_pandoc, mock_convert, mock_docx_file, temp_output_dir
    ):
        """Test basic DOCX to Markdown conversion."""
        # Setup mocks
        mock_get_pandoc.return_value = "/usr/bin/pandoc"
        mock_convert.return_value = None  # pypandoc writes to file

        output_path = temp_output_dir / "output.md"

        # Create a dummy markdown content for the output
        output_path.write_text("# Test Document\n\nThis is a test.")

        # Call converter
        result = convert_docx_to_markdown(
            input_path=mock_docx_file,
            output_path=output_path,
            extract_media=False,
        )

        # Assertions
        assert result == output_path
        mock_convert.assert_called_once()
        call_args = mock_convert.call_args
        assert str(mock_docx_file) == call_args[0][0]
        assert call_args[1]["to"] == "markdown"
        assert call_args[1]["format"] == "docx"

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.docx.to_markdown.pypandoc.convert_file")
    @patch("transmutation_codex.plugins.docx.to_markdown.get_pandoc_path")
    def test_convert_with_media_extraction(
        self, mock_get_pandoc, mock_convert, mock_docx_file, temp_output_dir
    ):
        """Test DOCX to Markdown conversion with media extraction."""
        # Setup mocks
        mock_get_pandoc.return_value = "/usr/bin/pandoc"
        mock_convert.return_value = None

        output_path = temp_output_dir / "output.md"
        output_path.write_text("# Test with media")

        # Call converter with media extraction
        result = convert_docx_to_markdown(
            input_path=mock_docx_file,
            output_path=output_path,
            extract_media=True,
        )

        # Assertions
        assert result == output_path
        mock_convert.assert_called_once()
        call_args = mock_convert.call_args

        # Check that extract-media argument is in extra_args
        extra_args = call_args[1]["extra_args"]
        assert any("--extract-media=" in arg for arg in extra_args)

    @pytest.mark.unit
    def test_file_not_found_error(self, temp_output_dir):
        """Test that converter raises FileNotFoundError for missing input."""
        non_existent = Path("/nonexistent/file.docx")
        output_path = temp_output_dir / "output.md"

        with pytest.raises(FileNotFoundError):
            convert_docx_to_markdown(
                input_path=non_existent,
                output_path=output_path,
            )

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.docx.to_markdown.get_pandoc_path")
    def test_pandoc_not_found_error(
        self, mock_get_pandoc, mock_docx_file, temp_output_dir
    ):
        """Test that converter raises error when Pandoc is not found."""
        # Make get_pandoc_path raise FileNotFoundError
        mock_get_pandoc.side_effect = FileNotFoundError("Pandoc not found")

        output_path = temp_output_dir / "output.md"

        with pytest.raises(FileNotFoundError, match="Pandoc not found"):
            convert_docx_to_markdown(
                input_path=mock_docx_file,
                output_path=output_path,
            )

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.docx.to_markdown.pypandoc.convert_file")
    @patch("transmutation_codex.plugins.docx.to_markdown.get_pandoc_path")
    def test_default_output_path(
        self, mock_get_pandoc, mock_convert, mock_docx_file, temp_output_dir
    ):
        """Test that default output path is generated correctly."""
        # Setup mocks
        mock_get_pandoc.return_value = "/usr/bin/pandoc"
        mock_convert.return_value = None

        # Expected output path should be input with .md extension
        expected_output = mock_docx_file.with_suffix(".md")
        expected_output.write_text("# Default path test")

        # Call converter without output_path
        result = convert_docx_to_markdown(
            input_path=mock_docx_file,
            extract_media=False,
        )

        # Assertions
        assert result == expected_output
        mock_convert.assert_called_once()
