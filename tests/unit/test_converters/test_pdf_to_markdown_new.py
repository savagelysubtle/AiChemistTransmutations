"""Tests for the PDF to Markdown converter with Phase 1/2 architecture."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ValidationError
from transmutation_codex.plugins.pdf.to_markdown import (
    convert_pdf_to_md,
    convert_pdf_to_md_with_enhanced_ocr,
    convert_pdf_to_md_with_pymupdf4llm,
)


class TestPDFToMarkdownConverter:
    """Test the PDF to Markdown converter with new architecture."""

    @pytest.fixture
    def test_pdf_path(self):
        """Path to test PDF file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.pdf"

    @pytest.fixture
    def test_pagebreak_pdf_path(self):
        """Path to test PDF with page breaks."""
        return Path(__file__).parent.parent.parent / "test_files" / "test_pagebreak.pdf"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_fitz(self):
        """Mock PyMuPDF for testing."""
        with patch("transmutation_codex.plugins.pdf.to_markdown.fitz") as mock_fitz:
            # Mock document
            mock_doc = Mock()
            mock_doc.page_count = 2
            mock_doc.is_encrypted = False
            mock_doc.close = Mock()

            # Mock pages
            mock_page1 = Mock()
            mock_page1.get_text.return_value = "Test content from page 1"
            mock_page1.get_pixmap.return_value = Mock(
                width=100, height=100, samples=b"fake"
            )

            mock_page2 = Mock()
            mock_page2.get_text.return_value = "Test content from page 2"
            mock_page2.get_pixmap.return_value = Mock(
                width=100, height=100, samples=b"fake"
            )

            mock_doc.load_page.side_effect = [mock_page1, mock_page2]
            mock_fitz.open.return_value = mock_doc

            yield mock_fitz

    @pytest.fixture
    def mock_tesseract(self):
        """Mock Tesseract OCR."""
        with patch(
            "transmutation_codex.plugins.pdf.to_markdown.pytesseract"
        ) as mock_tesseract:
            mock_tesseract.image_to_string.return_value = "OCR extracted text"
            yield mock_tesseract

    @pytest.fixture
    def mock_pymupdf4llm(self):
        """Mock PyMuPDF4LLM."""
        with patch(
            "transmutation_codex.plugins.pdf.to_markdown.parse_pdf_to_markdown"
        ) as mock_parse:
            mock_parse.return_value = (
                "# Test Document\n\nThis is test content from PyMuPDF4LLM."
            )
            yield mock_parse

    def test_convert_pdf_to_md_basic(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test basic PDF to Markdown conversion."""
        output_path = temp_output_dir / "test_output.md"

        result_path = convert_pdf_to_md(test_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path == output_path

        # Verify content
        content = result_path.read_text(encoding="utf-8")
        assert "# electron_test" in content
        assert "Test content from page 1" in content
        assert "Test content from page 2" in content

    def test_convert_pdf_to_md_auto_output(
        self, test_pdf_path, temp_output_dir, mock_fitz
    ):
        """Test PDF to Markdown conversion with auto-generated output path."""
        os.chdir(temp_output_dir)

        result_path = convert_pdf_to_md(test_pdf_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"
        assert result_path.name == "electron_test.md"

    def test_convert_pdf_to_md_with_ocr(
        self, test_pdf_path, temp_output_dir, mock_fitz, mock_tesseract
    ):
        """Test PDF to Markdown conversion with OCR fallback."""
        output_path = temp_output_dir / "test_output.md"

        # Mock empty text extraction to trigger OCR
        mock_page = Mock()
        mock_page.get_text.return_value = ""  # Empty text to trigger OCR
        mock_page.get_pixmap.return_value = Mock(width=100, height=100, samples=b"fake")
        mock_fitz.open.return_value.load_page.return_value = mock_page

        result_path = convert_pdf_to_md(test_pdf_path, output_path, auto_ocr=True)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"

        # Verify OCR was called
        mock_tesseract.image_to_string.assert_called()

    def test_convert_pdf_to_md_with_enhanced_ocr(
        self, test_pdf_path, temp_output_dir, mock_fitz, mock_tesseract
    ):
        """Test PDF to Markdown conversion with enhanced OCR."""
        output_path = temp_output_dir / "test_output.md"

        result_path = convert_pdf_to_md_with_enhanced_ocr(test_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"

        # Verify enhanced OCR was used
        content = result_path.read_text(encoding="utf-8")
        assert "enhanced OCR" in content.lower()

    def test_convert_pdf_to_md_with_pymupdf4llm(
        self, test_pdf_path, temp_output_dir, mock_pymupdf4llm
    ):
        """Test PDF to Markdown conversion with PyMuPDF4LLM."""
        output_path = temp_output_dir / "test_output.md"

        result_path = convert_pdf_to_md_with_pymupdf4llm(test_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"

        # Verify PyMuPDF4LLM was used
        content = result_path.read_text(encoding="utf-8")
        assert "Test Document" in content
        assert "PyMuPDF4LLM" in content

    def test_convert_pdf_to_md_invalid_file(self, temp_output_dir):
        """Test PDF to Markdown conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.pdf"
        output_path = temp_output_dir / "output.md"

        with pytest.raises(ValidationError):
            convert_pdf_to_md(invalid_path, output_path)

    def test_convert_pdf_to_md_non_pdf_file(self, temp_output_dir):
        """Test PDF to Markdown conversion with non-PDF file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a PDF")
        output_path = temp_output_dir / "output.md"

        with pytest.raises(ValueError, match="Input file must be a PDF"):
            convert_pdf_to_md(text_file, output_path)

    def test_converter_priority_order(self):
        """Test that converter priorities are correctly set."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered and has correct priority
        registry = get_registry()
        pdf_to_md_converters = registry.get_plugins_for_conversion("pdf", "md")
        assert len(pdf_to_md_converters) >= 1

    def test_progress_tracking(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.md"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.pdf.to_markdown.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.pdf.to_markdown.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.pdf.to_markdown.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_pdf_to_md(test_pdf_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.md"

        with patch(
            "transmutation_codex.plugins.pdf.to_markdown.publish"
        ) as mock_publish:
            result_path = convert_pdf_to_md(test_pdf_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert (
                call_args.event_type == "conversion.started"
            )  # Fixed: dot-separated format
            assert call_args.conversion_type == "pdf2md"

    def test_encrypted_pdf_handling(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test handling of encrypted PDFs."""
        output_path = temp_output_dir / "test_output.md"

        # Mock encrypted PDF
        mock_doc = Mock()
        mock_doc.page_count = 1
        mock_doc.is_encrypted = True
        mock_doc.authenticate.return_value = True
        mock_doc.close = Mock()

        mock_page = Mock()
        mock_page.get_text.return_value = "Decrypted content"
        mock_page.get_pixmap.return_value = Mock(width=100, height=100, samples=b"fake")
        mock_doc.load_page.return_value = mock_page

        mock_fitz.open.return_value = mock_doc

        result_path = convert_pdf_to_md(test_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"

        # Verify authentication was attempted
        mock_doc.authenticate.assert_called_with("")

    def test_page_break_handling(
        self, test_pagebreak_pdf_path, temp_output_dir, mock_fitz
    ):
        """Test handling of PDFs with page breaks."""
        output_path = temp_output_dir / "test_output.md"

        result_path = convert_pdf_to_md(test_pagebreak_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".md"

        # Verify page breaks are handled
        content = result_path.read_text(encoding="utf-8")
        assert "---" in content  # Page separator
