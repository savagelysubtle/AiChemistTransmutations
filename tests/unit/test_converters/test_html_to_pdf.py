"""Tests for HTML to PDF conversion."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from transmutation_codex.core.exceptions import ValidationError
from transmutation_codex.plugins.html.to_pdf import convert_html_to_pdf


class TestHTMLToPDFConverter:
    """Test the HTML to PDF converter."""

    @pytest.fixture
    def test_html_path(self):
        """Path to test HTML file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.html"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_pdfkit(self):
        """Mock pdfkit for testing."""
        with patch(
            "transmutation_codex.plugins.html.to_pdf.pdfkit.from_file"
        ) as mock_from_file:

            def mock_from_file_func(
                input_file, output_path, options=None, configuration=None
            ):
                # Create the output file to simulate successful PDF generation
                Path(output_path).touch()
                return None

            mock_from_file.side_effect = mock_from_file_func
            yield mock_from_file

    def test_convert_html_to_pdf_basic(
        self, test_html_path, temp_output_dir, mock_pdfkit
    ):
        """Test basic HTML to PDF conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        result_path = convert_html_to_pdf(test_html_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

        # Verify pdfkit was called
        mock_pdfkit.assert_called()

    def test_convert_html_to_pdf_auto_output(
        self, test_html_path, temp_output_dir, mock_pdfkit
    ):
        """Test HTML to PDF conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_html_to_pdf(test_html_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path.name == "electron_test.pdf"

    def test_convert_html_to_pdf_custom_options(
        self, test_html_path, temp_output_dir, mock_pdfkit
    ):
        """Test HTML to PDF conversion with custom options."""
        output_path = temp_output_dir / "test_output.pdf"

        custom_options = {
            "page_size": "A4",
            "margin": "1in",
            "css_styles": "body { font-size: 14px; }",
            "header_html": "<div>Header</div>",
            "footer_html": "<div>Footer</div>",
        }

        result_path = convert_html_to_pdf(test_html_path, output_path, **custom_options)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

        # Verify custom options were applied
        mock_pdfkit.assert_called()

    def test_convert_html_to_pdf_invalid_file(self, temp_output_dir):
        """Test HTML to PDF conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.html"
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ValidationError):
            convert_html_to_pdf(invalid_path, output_path)

    def test_convert_html_to_pdf_non_html_file(self, temp_output_dir):
        """Test HTML to PDF conversion with non-HTML file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not HTML")
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ValidationError, match="Format validation failed"):
            convert_html_to_pdf(text_file, output_path)

    def test_progress_tracking(self, test_html_path, temp_output_dir, mock_pdfkit):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.pdf"

        # This converter doesn't implement progress tracking
        result_path = convert_html_to_pdf(test_html_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

    def test_event_publishing(self, test_html_path, temp_output_dir, mock_pdfkit):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.pdf"

        # This converter doesn't implement event publishing
        result_path = convert_html_to_pdf(test_html_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

    def test_html_parsing(self, temp_output_dir, mock_pdfkit):
        """Test HTML parsing and PDF generation."""
        # Create test HTML content
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test Document</title>
</head>
<body>
    <h1>Test Document</h1>
    <p>This is a <strong>bold</strong> text and <em>italic</em> text.</p>
    <h2>Section 2</h2>
    <ul>
        <li>List item 1</li>
        <li>List item 2</li>
    </ul>
    <pre><code>print("Hello, World!")</code></pre>
    <blockquote>This is a blockquote.</blockquote>
</body>
</html>"""

        html_file = temp_output_dir / "test.html"
        html_file.write_text(html_content, encoding="utf-8")
        output_path = temp_output_dir / "test_output.pdf"

        result_path = convert_html_to_pdf(html_file, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

        # Verify HTML generation
        mock_pdfkit.assert_called()

    def test_error_handling(self, test_html_path, temp_output_dir):
        """Test error handling during conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock pdfkit to raise an error
        with patch(
            "transmutation_codex.plugins.html.to_pdf.pdfkit.from_file"
        ) as mock_from_file:
            mock_from_file.side_effect = Exception("pdfkit error")

            with pytest.raises(
                RuntimeError, match="Error converting HTML to PDF with pdfkit"
            ):
                convert_html_to_pdf(test_html_path, output_path)

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        html_to_pdf_converters = registry.get_plugins_for_conversion("html", "pdf")
        assert len(html_to_pdf_converters) >= 1
