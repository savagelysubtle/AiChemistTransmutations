"""Tests for Image to PDF conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.image.to_pdf import convert_image_to_pdf


class TestImageToPDFConverter:
    """Test the Image to PDF converter."""

    @pytest.fixture
    def test_image_path(self):
        """Path to test image file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.png"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_pil(self):
        """Mock PIL for testing."""
        with patch("transmutation_codex.plugins.image.to_pdf.Image") as mock_image:
            mock_img = Mock()
            mock_img.size = (100, 100)  # Mock image size
            mock_img.mode = "RGB"  # Mock image mode
            mock_img.convert.return_value = mock_img
            mock_img.save = Mock()

            # Make the mock support context manager protocol
            mock_img.__enter__ = Mock(return_value=mock_img)
            mock_img.__exit__ = Mock(return_value=None)

            mock_image.open.return_value = mock_img
            yield mock_image

    @pytest.fixture
    def mock_reportlab(self):
        """Mock ReportLab for testing."""
        with patch(
            "transmutation_codex.plugins.image.to_pdf.SimpleDocTemplate"
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

    def test_convert_image_to_pdf_basic(
        self, test_image_path, temp_output_dir, mock_pil, mock_reportlab
    ):
        """Test basic Image to PDF conversion."""
        output_path = temp_output_dir / "test_output.pdf"

        result_path = convert_image_to_pdf(test_image_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path == output_path

        # Verify PIL was called
        mock_pil.open.assert_called()

    def test_convert_image_to_pdf_auto_output(
        self, test_image_path, temp_output_dir, mock_pil, mock_reportlab
    ):
        """Test Image to PDF conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_image_to_pdf(test_image_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"
        assert result_path.name == "electron_test.pdf"

    def test_convert_image_to_pdf_custom_options(
        self, test_image_path, temp_output_dir, mock_pil, mock_reportlab
    ):
        """Test Image to PDF conversion with custom options."""
        output_path = temp_output_dir / "test_output.pdf"

        custom_options = {
            "quality": 95,
            "page_size": "A4",
            "margin": 0.5,
        }

        result_path = convert_image_to_pdf(
            test_image_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".pdf"

        # Verify custom options were applied
        mock_pil.open.assert_called()

    def test_convert_image_to_pdf_invalid_file(self, temp_output_dir):
        """Test Image to PDF conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.png"
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ValidationError):
            convert_image_to_pdf(invalid_path, output_path)

    def test_convert_image_to_pdf_non_image_file(self, temp_output_dir):
        """Test Image to PDF conversion with non-image file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an image")
        output_path = temp_output_dir / "output.pdf"

        with pytest.raises(ConversionError, match="Unsupported image format"):
            convert_image_to_pdf(text_file, output_path)

    def test_progress_tracking(
        self, test_image_path, temp_output_dir, mock_pil, mock_reportlab
    ):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.pdf"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.image.to_pdf.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.image.to_pdf.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.image.to_pdf.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_image_to_pdf(test_image_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id",
                {"output_path": str(output_path), "images_count": 1},
            )

    def test_event_publishing(
        self, test_image_path, temp_output_dir, mock_pil, mock_reportlab
    ):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.pdf"

        with patch("transmutation_codex.plugins.image.to_pdf.publish") as mock_publish:
            result_path = convert_image_to_pdf(test_image_path, output_path)

            # Verify event was published
            mock_publish.assert_called()
            call_args = mock_publish.call_args[0][0]
            assert call_args.event_type == "conversion.completed"
            assert call_args.conversion_type == "conversion"

    def test_converter_registration(self):
        """Test that the converter is properly registered."""
        from transmutation_codex.core import get_registry

        # Verify converter is registered
        registry = get_registry()
        image_to_pdf_converters = registry.get_plugins_for_conversion("image", "pdf")
        assert len(image_to_pdf_converters) >= 1
