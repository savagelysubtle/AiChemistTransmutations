"""Tests for EPUB to HTML conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ValidationError

from transmutation_codex.plugins.epub.to_html import convert_epub_to_html


class TestEPUBToHTMLConverter:
    """Test the EPUB to HTML converter."""

    @pytest.fixture
    def test_epub_path(self):
        """Path to test EPUB file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.epub"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_ebooklib(self):
        """Mock ebooklib for testing."""
        with patch(
            "transmutation_codex.plugins.epub.to_html.ebooklib"
        ) as mock_ebooklib:
            mock_book = Mock()
            mock_ebooklib.EpubReader.return_value = mock_book
            mock_book.get_items.return_value = [
                Mock(
                    content=b"<html><body>Test content</body></html>",
                    media_type="application/xhtml+xml",
                )
            ]
            yield mock_ebooklib

    def test_convert_epub_to_html_basic(
        self, test_epub_path, temp_output_dir, mock_ebooklib
    ):
        """Test basic EPUB to HTML conversion."""
        output_path = temp_output_dir / "test_output.html"

        result_path = convert_epub_to_html(test_epub_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path == output_path

        # Verify HTML content
        content = result_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "<html>" in content
        assert "<body>" in content
        assert "Test content" in content

    def test_convert_epub_to_html_auto_output(
        self, test_epub_path, temp_output_dir, mock_ebooklib
    ):
        """Test EPUB to HTML conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_epub_to_html(test_epub_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path.name == "electron_test.html"

    def test_convert_epub_to_html_custom_options(
        self, test_epub_path, temp_output_dir, mock_ebooklib
    ):
        """Test EPUB to HTML conversion with custom options."""
        output_path = temp_output_dir / "test_output.html"

        custom_options = {
            "css_styles": "body { font-size: 14px; color: #333; }",
            "include_images": True,
            "metadata": {"title": "Custom Title", "author": "Test Author"},
        }

        result_path = convert_epub_to_html(
            test_epub_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        assert "font-size: 14px" in content
        assert "Custom Title" in content

    def test_convert_epub_to_html_invalid_file(self, temp_output_dir):
        """Test EPUB to HTML conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.epub"
        output_path = temp_output_dir / "output.html"

        with pytest.raises(ValidationError):
            convert_epub_to_html(invalid_path, output_path)

    def test_convert_epub_to_html_non_epub_file(self, temp_output_dir):
        """Test EPUB to HTML conversion with non-EPUB file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an EPUB")
        output_path = temp_output_dir / "output.html"

        with pytest.raises(ValueError, match="Input file must be an EPUB file"):
            convert_epub_to_html(text_file, output_path)

    def test_progress_tracking(self, test_epub_path, temp_output_dir, mock_ebooklib):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.html"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.epub.to_html.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.epub.to_html.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.epub.to_html.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_epub_to_html(test_epub_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with("test_operation_id", {"output_path": str(output_path)})

    def test_event_publishing(self, test_epub_path, temp_output_dir, mock_ebooklib):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.html"

        with patch("transmutation_codex.plugins.epub.to_html.publish") as mock_publish:
            result_path = convert_epub_to_html(test_epub_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "epub2html"

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        epub_to_html_converters = registry.get_plugins_for_conversion("epub", "html")
        assert len(epub_to_html_converters) >= 1
