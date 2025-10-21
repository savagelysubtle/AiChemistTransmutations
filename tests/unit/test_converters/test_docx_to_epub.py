"""Tests for DOCX to EPUB conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.docx.to_epub import convert_docx_to_epub


class TestDOCXToEPUBConverter:
    """Test the DOCX to EPUB converter."""

    @pytest.fixture
    def test_docx_path(self):
        """Path to test DOCX file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.docx"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_ebooklib(self):
        """Mock ebooklib for testing."""
        with patch("transmutation_codex.plugins.docx.to_epub.epub") as mock_epub:
            mock_book = Mock()
            mock_epub.EpubBook.return_value = mock_book
            mock_epub.EpubHtml.return_value = Mock()
            mock_epub.EpubNcx.return_value = Mock()
            mock_epub.EpubNav.return_value = Mock()

            # Mock write_epub to simulate file creation
            mock_write_epub = Mock()

            def write_epub_side_effect(output_path, book, options):
                Path(output_path).touch()

            mock_write_epub.side_effect = write_epub_side_effect
            mock_epub.write_epub = mock_write_epub
            yield mock_epub

    @pytest.fixture
    def mock_docx(self):
        """Mock python-docx for testing."""
        with patch("transmutation_codex.plugins.docx.to_epub.Document") as mock_docx:
            mock_doc = Mock()
            mock_docx.return_value = mock_doc

            # Create mock paragraph with proper style attribute
            mock_paragraph = Mock()
            mock_paragraph.text = "Test paragraph"
            mock_paragraph.style.name = "Normal"  # Set style name as string

            mock_doc.paragraphs = [mock_paragraph]
            mock_doc.tables = []
            yield mock_docx

    def test_convert_docx_to_epub_basic(
        self, test_docx_path, temp_output_dir, mock_ebooklib, mock_docx
    ):
        """Test basic DOCX to EPUB conversion."""
        output_path = temp_output_dir / "test_output.epub"

        result_path = convert_docx_to_epub(test_docx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".epub"
        assert result_path == output_path

        # Verify EPUB was created
        mock_ebooklib.write_epub.assert_called()

    def test_convert_docx_to_epub_auto_output(
        self, test_docx_path, temp_output_dir, mock_ebooklib, mock_docx
    ):
        """Test DOCX to EPUB conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_docx_to_epub(test_docx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".epub"
        assert result_path.name == "electron_test.epub"

    def test_convert_docx_to_epub_custom_options(
        self, test_docx_path, temp_output_dir, mock_ebooklib, mock_docx
    ):
        """Test DOCX to EPUB conversion with custom options."""
        output_path = temp_output_dir / "test_output.epub"

        custom_options = {
            "title": "Custom Title",
            "author": "Test Author",
            "language": "en",
            "cover_image": None,
            "css_styles": "body { font-size: 14px; }",
        }

        result_path = convert_docx_to_epub(
            test_docx_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".epub"

        # Verify custom options were applied
        mock_ebooklib.write_epub.assert_called()

    def test_convert_docx_to_epub_invalid_file(self, temp_output_dir):
        """Test DOCX to EPUB conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.docx"
        output_path = temp_output_dir / "output.epub"

        with pytest.raises(ValidationError):
            convert_docx_to_epub(invalid_path, output_path)

    def test_convert_docx_to_epub_non_docx_file(self, temp_output_dir):
        """Test DOCX to EPUB conversion with non-DOCX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a DOCX")
        output_path = temp_output_dir / "output.epub"

        with pytest.raises(ConversionError, match="Failed to load DOCX file"):
            convert_docx_to_epub(text_file, output_path)

    def test_progress_tracking(
        self, test_docx_path, temp_output_dir, mock_ebooklib, mock_docx
    ):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.epub"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.docx.to_epub.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.docx.to_epub.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.docx.to_epub.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_docx_to_epub(test_docx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(
        self, test_docx_path, temp_output_dir, mock_ebooklib, mock_docx
    ):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.epub"

        with patch("transmutation_codex.plugins.docx.to_epub.publish") as mock_publish:
            result_path = convert_docx_to_epub(test_docx_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "docx2epub"

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        docx_to_epub_converters = registry.get_plugins_for_conversion("docx", "epub")
        assert len(docx_to_epub_converters) >= 1
