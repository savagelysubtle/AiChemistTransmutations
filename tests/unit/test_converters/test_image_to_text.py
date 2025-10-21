"""Tests for Image to Text conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.image.to_text import convert_image_to_text


class TestImageToTextConverter:
    """Test the Image to Text converter."""

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
    def mock_tesseract(self):
        """Mock Tesseract OCR for testing."""
        with patch(
            "transmutation_codex.plugins.image.to_text.pytesseract"
        ) as mock_tesseract:
            mock_tesseract.image_to_string.return_value = (
                "OCR extracted text from image"
            )
            yield mock_tesseract

    @pytest.fixture
    def mock_pil(self):
        """Mock PIL for testing."""
        with patch("transmutation_codex.plugins.image.to_text.Image") as mock_image:
            mock_img = Mock()
            mock_image.open.return_value = mock_img
            yield mock_image

    def test_convert_image_to_text_basic(
        self, test_image_path, temp_output_dir, mock_tesseract, mock_pil
    ):
        """Test basic Image to Text conversion."""
        output_path = temp_output_dir / "test_output.txt"

        result_path = convert_image_to_text(test_image_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".txt"
        assert result_path == output_path

        # Verify text content
        content = result_path.read_text(encoding="utf-8")
        assert "OCR extracted text from image" in content

        # Verify Tesseract was called
        mock_tesseract.image_to_string.assert_called()

    def test_convert_image_to_text_auto_output(
        self, test_image_path, temp_output_dir, mock_tesseract, mock_pil
    ):
        """Test Image to Text conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_image_to_text(test_image_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".txt"
        assert result_path.name == "electron_test.txt"

    def test_convert_image_to_text_custom_options(
        self, test_image_path, temp_output_dir, mock_tesseract, mock_pil
    ):
        """Test Image to Text conversion with custom options."""
        output_path = temp_output_dir / "test_output.txt"

        custom_options = {
            "language": "eng",
            "dpi": 300,
            "psm": 1,
            "oem": 3,
            "encoding": "utf-8",
        }

        result_path = convert_image_to_text(
            test_image_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".txt"

        # Verify custom options were applied
        mock_tesseract.image_to_string.assert_called()

    def test_convert_image_to_text_invalid_file(self, temp_output_dir):
        """Test Image to Text conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.png"
        output_path = temp_output_dir / "output.txt"

        with pytest.raises(ValidationError):
            convert_image_to_text(invalid_path, output_path)

    def test_convert_image_to_text_non_image_file(self, temp_output_dir):
        """Test Image to Text conversion with non-image file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an image")
        output_path = temp_output_dir / "output.txt"

        with pytest.raises(ConversionError, match="Conversion failed"):
            convert_image_to_text(text_file, output_path)

    def test_progress_tracking(
        self, test_image_path, temp_output_dir, mock_tesseract, mock_pil
    ):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.txt"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.image.to_text.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.image.to_text.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.image.to_text.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_image_to_text(test_image_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(
        self, test_image_path, temp_output_dir, mock_tesseract, mock_pil
    ):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.txt"

        with patch("transmutation_codex.plugins.image.to_text.publish") as mock_publish:
            result_path = convert_image_to_text(test_image_path, output_path)

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
        image_to_text_converters = registry.get_plugins_for_conversion("image", "text")
        assert len(image_to_text_converters) >= 1
