"""Tests for PDF to HTML conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.plugins.pdf.to_html import convert_pdf_to_html


class TestPDFToHTMLConverter:
    """Test the PDF to HTML converter."""

    @pytest.fixture
    def test_pdf_path(self):
        """Path to test PDF file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.pdf"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_fitz(self):
        """Mock PyMuPDF for testing."""
        with patch("transmutation_codex.plugins.pdf.to_html.fitz") as mock_fitz:
            # Mock document
            mock_doc = Mock()
            mock_doc.page_count = 2
            mock_doc.is_encrypted = False
            mock_doc.close = Mock()
            mock_doc.__len__ = Mock(return_value=2)  # Make it len() compatible

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

    def test_convert_pdf_to_html_basic(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test basic PDF to HTML conversion."""
        output_path = temp_output_dir / "test_output.html"

        result_path = convert_pdf_to_html(test_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path == output_path

        # Verify HTML content
        content = result_path.read_text(encoding="utf-8")
        assert "<html>" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "Test content from page 1" in content
        assert "Test content from page 2" in content

    def test_convert_pdf_to_html_auto_output(
        self, test_pdf_path, temp_output_dir, mock_fitz
    ):
        """Test PDF to HTML conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_pdf_to_html(test_pdf_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path.name == "electron_test.html"

    def test_convert_pdf_to_html_custom_options(
        self, test_pdf_path, temp_output_dir, mock_fitz
    ):
        """Test PDF to HTML conversion with custom options."""
        output_path = temp_output_dir / "test_output.html"

        custom_options = {
            "css_styles": "body { font-size: 14px; color: #333; }",
            "include_images": True,
            "image_format": "png",
            "metadata": {"title": "Custom Title", "author": "Test Author"},
        }

        result_path = convert_pdf_to_html(test_pdf_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        assert "<html>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_convert_pdf_to_html_invalid_file(self, temp_output_dir):
        """Test PDF to HTML conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.pdf"
        output_path = temp_output_dir / "output.html"

        with pytest.raises(RuntimeError, match="Error converting PDF to HTML"):
            convert_pdf_to_html(invalid_path, output_path)

    def test_convert_pdf_to_html_non_pdf_file(self, temp_output_dir):
        """Test PDF to HTML conversion with non-PDF file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a PDF")
        output_path = temp_output_dir / "output.html"

        with pytest.raises(RuntimeError, match="Error converting PDF to HTML"):
            convert_pdf_to_html(text_file, output_path)

    def test_progress_tracking(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.html"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.pdf.to_html.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.pdf.to_html.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.pdf.to_html.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_pdf_to_html(test_pdf_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with("test_operation_id", success=True)

    def test_event_publishing(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.html"

        with patch("transmutation_codex.plugins.pdf.to_html.publish") as mock_publish:
            result_path = convert_pdf_to_html(test_pdf_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "pdf2html"

    def test_encrypted_pdf_handling(self, test_pdf_path, temp_output_dir, mock_fitz):
        """Test handling of encrypted PDFs."""
        output_path = temp_output_dir / "test_output.html"

        # Mock encrypted PDF
        mock_doc = Mock()
        mock_doc.page_count = 1
        mock_doc.is_encrypted = True
        mock_doc.authenticate.return_value = True
        mock_doc.close = Mock()
        mock_doc.__len__ = Mock(return_value=1)  # Make it len() compatible

        mock_page = Mock()
        mock_page.get_text.return_value = "Decrypted content"
        mock_page.get_pixmap.return_value = Mock(width=100, height=100, samples=b"fake")
        mock_doc.load_page.return_value = mock_page

        mock_fitz.open.return_value = mock_doc

        result_path = convert_pdf_to_html(test_pdf_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify authentication was attempted
        mock_doc.authenticate.assert_called_with("")

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        pdf_to_html_converters = registry.get_plugins_for_conversion("pdf", "html")
        assert len(pdf_to_html_converters) >= 1
