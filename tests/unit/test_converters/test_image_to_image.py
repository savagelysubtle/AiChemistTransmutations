"""Tests for Image to Image conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.image.to_image import convert_image_to_image


class TestImageToImageConverter:
    """Test the Image to Image converter."""

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
        with patch("transmutation_codex.plugins.image.to_image.Image") as mock_image:
            mock_img = Mock()
            mock_img.size = (100, 100)  # Mock image size
            mock_img.mode = "RGB"  # Mock image mode
            mock_img.width = 100
            mock_img.height = 100
            mock_img.convert.return_value = mock_img
            mock_img.resize.return_value = mock_img
            mock_img.rotate.return_value = mock_img
            mock_img.transpose.return_value = mock_img
            mock_img.filter.return_value = mock_img
            mock_img.split.return_value = [Mock(), Mock(), Mock(), Mock()]
            mock_img.save = Mock()

            # Make the mock support context manager protocol
            mock_img.__enter__ = Mock(return_value=mock_img)
            mock_img.__exit__ = Mock(return_value=None)

            mock_image.open.return_value = mock_img
            mock_image.new.return_value = mock_img

            # Mock ImageOps
            with patch(
                "transmutation_codex.plugins.image.to_image.ImageOps"
            ) as mock_imageops:
                mock_imageops.fit.return_value = mock_img

                # Mock ImageEnhance
                with patch(
                    "transmutation_codex.plugins.image.to_image.ImageEnhance"
                ) as mock_imageenhance:
                    mock_enhancer = Mock()
                    mock_enhancer.enhance.return_value = mock_img
                    mock_imageenhance.Brightness.return_value = mock_enhancer
                    mock_imageenhance.Contrast.return_value = mock_enhancer
                    mock_imageenhance.Color.return_value = mock_enhancer
                    mock_imageenhance.Sharpness.return_value = mock_enhancer

                    # Mock ImageFilter
                    with patch(
                        "transmutation_codex.plugins.image.to_image.ImageFilter"
                    ) as mock_imagefilter:
                        mock_imagefilter.BLUR = Mock()
                        mock_imagefilter.SHARPEN = Mock()
                        mock_imagefilter.EDGE_ENHANCE = Mock()
                        mock_imagefilter.EMBOSS = Mock()

                        # Mock the save method to create the output file
                        def mock_save(path, format=None, **kwargs):
                            Path(path).touch()

                        mock_img.save = mock_save
                        yield mock_image

    def test_convert_image_to_image_basic(
        self, test_image_path, temp_output_dir, mock_pil
    ):
        """Test basic Image to Image conversion."""
        output_path = temp_output_dir / "test_output.jpg"

        result_path = convert_image_to_image(test_image_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".jpg"
        assert result_path == output_path

        # Verify PIL was called
        mock_pil.open.assert_called()

    def test_convert_image_to_image_auto_output(
        self, test_image_path, temp_output_dir, mock_pil
    ):
        """Test Image to Image conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_image_to_image(test_image_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".png"  # Default format
        assert result_path.name == "electron_test.png"

    def test_convert_image_to_image_custom_options(
        self, test_image_path, temp_output_dir, mock_pil
    ):
        """Test Image to Image conversion with custom options."""
        output_path = temp_output_dir / "test_output.png"

        custom_options = {
            "output_format": "PNG",
            "quality": 95,
            "resize": "800,600",
            "resize_mode": "fit",
        }

        result_path = convert_image_to_image(
            test_image_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".png"

        # Verify custom options were applied
        mock_pil.open.assert_called()

    def test_convert_image_to_image_invalid_file(self, temp_output_dir):
        """Test Image to Image conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.png"
        output_path = temp_output_dir / "output.jpg"

        with pytest.raises(ValidationError):
            convert_image_to_image(invalid_path, output_path)

    def test_convert_image_to_image_non_image_file(self, temp_output_dir):
        """Test Image to Image conversion with non-image file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not an image")
        output_path = temp_output_dir / "output.jpg"

        with pytest.raises(ConversionError, match="Failed to process image"):
            convert_image_to_image(text_file, output_path)

    def test_progress_tracking(self, test_image_path, temp_output_dir, mock_pil):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.jpg"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.image.to_image.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.image.to_image.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.image.to_image.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_image_to_image(test_image_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            mock_complete.assert_called_once_with(
                "test_operation_id", {"output_path": str(output_path)}
            )

    def test_event_publishing(self, test_image_path, temp_output_dir, mock_pil):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.jpg"

        with patch(
            "transmutation_codex.plugins.image.to_image.publish"
        ) as mock_publish:
            result_path = convert_image_to_image(test_image_path, output_path)

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
        image_to_image_converters = registry.get_plugins_for_conversion(
            "image", "image"
        )
        assert len(image_to_image_converters) >= 1
