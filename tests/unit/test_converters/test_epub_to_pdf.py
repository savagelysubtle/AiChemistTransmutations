"""Tests for EPUB to PDF conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.epub.to_pdf import convert_epub_to_pdf


class TestEPUBToPDFConverter:
    """Test the EPUB to PDF converter."""

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
            "transmutation_codex.plugins.epub.to_pdf.epub.read_epub"
        ) as mock_read_epub:
            mock_book = Mock()
            mock_read_epub.return_value = mock_book

            # Mock metadata methods to return proper structure
            mock_book.get_metadata.return_value = [("Test Book Title",)]
            mock_book.get_items.return_value = [
                Mock(
                    content=b"<html><body>Test content</body></html>",
                    media_type="application/xhtml+xml",
                )
            ]
            # Mock spine to return iterable list of tuples
            mock_book.spine = [("item1", "linear"), ("item2", "linear")]

            # Mock get_item_with_id to return mock items with get_name and get_content methods
            def mock_get_item_with_id(item_id):
                mock_item = Mock()
                mock_item.get_name.return_value = f"Chapter {item_id}"
                mock_item.get_content.return_value = (
                    b"<html><body><p>Test chapter content</p></body></html>"
                )
                return mock_item

            mock_book.get_item_with_id = mock_get_item_with_id
            yield mock_read_epub

    @pytest.fixture
    def mock_reportlab(self):
        """Mock ReportLab for testing."""
        with patch(
            "transmutation_codex.plugins.epub.to_pdf.SimpleDocTemplate"
        ) as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance

            # Mock the build method to create the output file
            def mock_build(story):
                # Create the output file to simulate successful PDF generation
                output_path = mock_doc.call_args[0][
                    0
                ]  # First argument is the output path
                Path(output_path).touch()

            mock_doc_instance.build = mock_build
            yield mock_doc

    def test_convert_epub_to_pdf_basic(
        self, test_epub_path, temp_output_dir, mock_ebooklib, mock_reportlab
    ):
        """Test basic EPUB to PDF conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        result_path = convert_epub_to_pdf(test_epub_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

        # Verify WeasyPrint was called
        mock_reportlab.assert_called()

    def test_convert_epub_to_pdf_auto_output(
        self, test_epub_path, temp_output_dir, mock_ebooklib, mock_reportlab
    ):
        """Test EPUB to PDF conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_epub_to_pdf(test_epub_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path.name == "electron_test.pdf"

    def test_convert_epub_to_pdf_custom_options(
        self, test_epub_path, temp_output_dir, mock_ebooklib, mock_reportlab
    ):
        """Test EPUB to PDF conversion with custom options."""
        output_path = temp_output_dir / "test_output.pdf"

        custom_options = {
            "page_size": "A4",
            "margin": 1.0,  # Convert to float
            "css_styles": "body { font-size: 14px; }",
            "header_html": "<div>Header</div>",
            "footer_html": "<div>Footer</div>",
        }

        result_path = convert_epub_to_pdf(test_epub_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

        # Verify custom options were applied
        mock_reportlab.assert_called()

    def test_convert_epub_to_pdf_invalid_file(self, temp_output_dir):
        """Test EPUB to PDF conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.epub"
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ValidationError):
            convert_epub_to_pdf(invalid_path, output_path)

    def test_convert_epub_to_pdf_non_epub_file(self, temp_output_dir):
        """Test EPUB to PDF conversion with non-EPUB file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an EPUB")
        output_path = temp_output_dir / "output.pdf"

        # The converter expects a valid EPUB/ZIP file
        with pytest.raises(ConversionError, match="Failed to load EPUB file"):
            convert_epub_to_pdf(text_file, output_path)

    def test_progress_tracking(
        self, test_epub_path, temp_output_dir, mock_ebooklib, mock_reportlab
    ):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.epub.to_pdf.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.epub.to_pdf.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.epub.to_pdf.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_epub_to_pdf(test_epub_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(
        self, test_epub_path, temp_output_dir, mock_ebooklib, mock_reportlab
    ):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.pdf"

        with patch("transmutation_codex.plugins.epub.to_pdf.publish") as mock_publish:
            result_path = convert_epub_to_pdf(test_epub_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "epub2pdf"

    def test_error_handling(self, test_epub_path, temp_output_dir, mock_ebooklib):
        """Test error handling during conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock ReportLab to raise an error
        with patch(
            "transmutation_codex.plugins.epub.to_pdf.SimpleDocTemplate"
        ) as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            mock_doc_instance.build.side_effect = Exception("ReportLab error")

            with pytest.raises(ConversionError, match="EPUB to PDF conversion failed"):
                convert_epub_to_pdf(test_epub_path, output_path)

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        epub_to_pdf_converters = registry.get_plugins_for_conversion("epub", "pdf")
        assert len(epub_to_pdf_converters) >= 1
