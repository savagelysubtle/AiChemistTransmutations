"""Tests for EPUB to DOCX converter."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from transmutation_codex.core.exceptions import ValidationError

# Mock dependencies before importing
sys.modules["ebooklib"] = MagicMock()
sys.modules["ebooklib.epub"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["docx"] = MagicMock()
sys.modules["docx.enum"] = MagicMock()
sys.modules["docx.enum.text"] = MagicMock()
sys.modules["docx.shared"] = MagicMock()

from transmutation_codex.plugins.epub.to_docx import convert_epub_to_docx


class TestEPUBToDOCXConverter:
    """Test the EPUB to DOCX converter."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_epub_file(self, tmp_path):
        """Create a mock EPUB file for testing."""
        epub_path = tmp_path / "test.epub"
        # Create a minimal EPUB file (just touch it for testing)
        epub_path.touch()
        return epub_path

    @pytest.fixture
    def mock_epub_book(self):
        """Create a mock EPUB book object."""
        book = MagicMock()
        book.get_metadata.side_effect = lambda ns, key: {
            "title": [["Test Book"]],
            "creator": [["Test Author"]],
            "description": [["Test Description"]],
        }.get(key, [[]])

        # Mock spine items
        item1 = MagicMock()
        item1.get_name.return_value = "Chapter 1"
        item1.get_content.return_value = b"<html><body><p>Chapter 1 content</p></body></html>"

        item2 = MagicMock()
        item2.get_name.return_value = "Chapter 2"
        item2.get_content.return_value = b"<html><body><p>Chapter 2 content</p></body></html>"

        book.spine = [("item1", None), ("item2", None)]
        book.get_item_by_id.side_effect = lambda item_id: {
            "item1": item1,
            "item2": item2,
        }.get(item_id)

        return book

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.epub.to_docx.epub.read_epub")
    @patch("transmutation_codex.plugins.epub.to_docx.Document")
    @patch("transmutation_codex.plugins.epub.to_docx.check_feature_access")
    @patch("transmutation_codex.plugins.epub.to_docx.check_file_size_limit")
    @patch("transmutation_codex.plugins.epub.to_docx.record_conversion_attempt")
    def test_convert_epub_to_docx_basic(
        self,
        mock_record,
        mock_size_check,
        mock_feature_access,
        mock_document,
        mock_read_epub,
        mock_epub_file,
        mock_epub_book,
        temp_output_dir,
    ):
        """Test basic EPUB to DOCX conversion."""
        # Setup mocks
        mock_read_epub.return_value = mock_epub_book
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        output_path = temp_output_dir / "output.docx"

        # Call converter
        result = convert_epub_to_docx(
            input_path=mock_epub_file,
            output_path=output_path,
            include_toc=True,
            chapter_breaks=True,
        )

        # Assertions
        assert result == output_path
        mock_read_epub.assert_called_once_with(str(mock_epub_file))
        mock_doc_instance.save.assert_called_once_with(str(output_path))
        mock_feature_access.assert_called_once_with("epub2docx")
        mock_size_check.assert_called_once()
        mock_record.assert_called_once_with("epub2docx")

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.epub.to_docx.epub.read_epub")
    @patch("transmutation_codex.plugins.epub.to_docx.Document")
    @patch("transmutation_codex.plugins.epub.to_docx.check_feature_access")
    @patch("transmutation_codex.plugins.epub.to_docx.check_file_size_limit")
    @patch("transmutation_codex.plugins.epub.to_docx.record_conversion_attempt")
    def test_convert_without_metadata(
        self,
        mock_record,
        mock_size_check,
        mock_feature_access,
        mock_document,
        mock_read_epub,
        mock_epub_file,
        mock_epub_book,
        temp_output_dir,
    ):
        """Test EPUB to DOCX conversion without metadata."""
        # Setup mocks
        mock_read_epub.return_value = mock_epub_book
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        output_path = temp_output_dir / "output.docx"

        # Call converter without metadata
        result = convert_epub_to_docx(
            input_path=mock_epub_file,
            output_path=output_path,
            include_metadata=False,
            include_toc=False,
        )

        # Assertions
        assert result == output_path
        mock_doc_instance.save.assert_called_once_with(str(output_path))

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.epub.to_docx.epub.read_epub")
    @patch("transmutation_codex.plugins.epub.to_docx.Document")
    @patch("transmutation_codex.plugins.epub.to_docx.check_feature_access")
    @patch("transmutation_codex.plugins.epub.to_docx.check_file_size_limit")
    @patch("transmutation_codex.plugins.epub.to_docx.record_conversion_attempt")
    def test_custom_font_settings(
        self,
        mock_record,
        mock_size_check,
        mock_feature_access,
        mock_document,
        mock_read_epub,
        mock_epub_file,
        mock_epub_book,
        temp_output_dir,
    ):
        """Test EPUB to DOCX conversion with custom font settings."""
        # Setup mocks
        mock_read_epub.return_value = mock_epub_book
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        output_path = temp_output_dir / "output.docx"

        # Call converter with custom font
        result = convert_epub_to_docx(
            input_path=mock_epub_file,
            output_path=output_path,
            font_name="Arial",
            font_size=14,
        )

        # Assertions
        assert result == output_path
        mock_doc_instance.save.assert_called_once_with(str(output_path))

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.epub.to_docx.epub.read_epub")
    @patch("transmutation_codex.plugins.epub.to_docx.check_feature_access")
    @patch("transmutation_codex.plugins.epub.to_docx.check_file_size_limit")
    def test_epub_read_failure(
        self,
        mock_size_check,
        mock_feature_access,
        mock_read_epub,
        mock_epub_file,
        temp_output_dir,
    ):
        """Test that converter handles EPUB reading errors."""
        # Make read_epub raise an exception
        mock_read_epub.side_effect = Exception("Failed to read EPUB")

        output_path = temp_output_dir / "output.docx"

        # Should raise ConversionError
        from transmutation_codex.core.exceptions import ConversionError

        with pytest.raises(ConversionError):
            convert_epub_to_docx(
                input_path=mock_epub_file,
                output_path=output_path,
            )

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.epub.to_docx.epub.read_epub")
    @patch("transmutation_codex.plugins.epub.to_docx.Document")
    @patch("transmutation_codex.plugins.epub.to_docx.check_feature_access")
    @patch("transmutation_codex.plugins.epub.to_docx.check_file_size_limit")
    @patch("transmutation_codex.plugins.epub.to_docx.record_conversion_attempt")
    def test_default_output_path(
        self,
        mock_record,
        mock_size_check,
        mock_feature_access,
        mock_document,
        mock_read_epub,
        mock_epub_file,
        mock_epub_book,
    ):
        """Test that default output path is generated correctly."""
        # Setup mocks
        mock_read_epub.return_value = mock_epub_book
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        # Expected output path should be input with .docx extension
        expected_output = mock_epub_file.with_suffix(".docx")

        # Call converter without output_path
        result = convert_epub_to_docx(
            input_path=mock_epub_file,
        )

        # Assertions
        assert result == expected_output
        mock_doc_instance.save.assert_called_once_with(str(expected_output))

    @pytest.mark.unit
    @patch("transmutation_codex.plugins.epub.to_docx.epub.read_epub")
    @patch("transmutation_codex.plugins.epub.to_docx.Document")
    @patch("transmutation_codex.plugins.epub.to_docx.check_feature_access")
    @patch("transmutation_codex.plugins.epub.to_docx.check_file_size_limit")
    @patch("transmutation_codex.plugins.epub.to_docx.record_conversion_attempt")
    def test_preserve_formatting(
        self,
        mock_record,
        mock_size_check,
        mock_feature_access,
        mock_document,
        mock_read_epub,
        mock_epub_file,
        mock_epub_book,
        temp_output_dir,
    ):
        """Test EPUB to DOCX conversion with formatting preservation."""
        # Setup mocks with formatted content
        book = MagicMock()
        book.get_metadata.return_value = [[]]

        item1 = MagicMock()
        item1.get_name.return_value = "Chapter 1"
        item1.get_content.return_value = (
            b"<html><body>"
            b"<p><strong>Bold text</strong> and <em>italic text</em></p>"
            b"</body></html>"
        )

        book.spine = [("item1", None)]
        book.get_item_by_id.return_value = item1

        mock_read_epub.return_value = book
        mock_doc_instance = MagicMock()
        mock_document.return_value = mock_doc_instance

        output_path = temp_output_dir / "output.docx"

        # Call converter with formatting preservation
        result = convert_epub_to_docx(
            input_path=mock_epub_file,
            output_path=output_path,
            preserve_formatting=True,
        )

        # Assertions
        assert result == output_path
        mock_doc_instance.save.assert_called_once_with(str(output_path))

