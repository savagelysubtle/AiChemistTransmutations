"""Tests for PPTX to Images conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.pptx.to_images import convert_pptx_to_images


class TestPPTXToImagesConverter:
    """Test the PPTX to Images converter."""

    @pytest.fixture
    def test_pptx_path(self):
        """Path to test PPTX file."""
        return Path(__file__).parent.parent.parent / "test_files" / "electron_test.pptx"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    @pytest.fixture
    def mock_python_pptx(self):
        """Mock python-pptx for testing."""
        with patch(
            "transmutation_codex.plugins.pptx.to_images.Presentation"
        ) as mock_presentation:
            mock_pres = Mock()
            mock_presentation.return_value = mock_pres

            # Create mock slide with shapes
            mock_slide = Mock()
            mock_shape = Mock()
            mock_shape.text = "Test slide content"
            mock_slide.shapes = [mock_shape]

            mock_pres.slides = [mock_slide]
            yield mock_presentation

    def test_convert_pptx_to_images_basic(
        self, test_pptx_path, temp_output_dir, mock_python_pptx
    ):
        """Test basic PPTX to Images conversion."""
        output_path = temp_output_dir / "test_output"

        result_path = convert_pptx_to_images(test_pptx_path, output_path)

        # Verify output
        assert isinstance(result_path, Path)
        assert result_path.exists()
        assert result_path.is_dir()

        # Check that image files were created in the output directory
        image_files = (
            list(result_path.glob("*.png"))
            + list(result_path.glob("*.jpg"))
            + list(result_path.glob("*.jpeg"))
        )
        assert len(image_files) > 0

    def test_convert_pptx_to_images_auto_output(
        self, test_pptx_path, temp_output_dir, mock_python_pptx
    ):
        """Test PPTX to Images conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_pptx_to_images(test_pptx_path)

        # Verify output
        assert isinstance(result_path, Path)
        assert result_path.exists()
        assert result_path.is_dir()

        # Check that image files were created in the output directory
        image_files = (
            list(result_path.glob("*.png"))
            + list(result_path.glob("*.jpg"))
            + list(result_path.glob("*.jpeg"))
        )
        assert len(image_files) > 0

    def test_convert_pptx_to_images_custom_options(
        self, test_pptx_path, temp_output_dir, mock_python_pptx
    ):
        """Test PPTX to Images conversion with custom options."""
        output_path = temp_output_dir / "test_output"

        custom_options = {
            "image_format": "png",
            "slide_range": "1-3",
            "quality": "high",
            "dpi": 300,
        }

        result_path = convert_pptx_to_images(
            test_pptx_path, output_path, **custom_options
        )

        # Verify output
        assert isinstance(result_path, Path)
        assert result_path.exists()
        assert result_path.is_dir()

        # Check that image files were created in the output directory
        image_files = (
            list(result_path.glob("*.png"))
            + list(result_path.glob("*.jpg"))
            + list(result_path.glob("*.jpeg"))
        )
        assert len(image_files) > 0

    def test_convert_pptx_to_images_invalid_file(self, temp_output_dir):
        """Test PPTX to Images conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.pptx"
        output_path = temp_output_dir / "output"

        with pytest.raises(ValidationError):
            convert_pptx_to_images(invalid_path, output_path)

    def test_convert_pptx_to_images_non_pptx_file(self, temp_output_dir):
        """Test PPTX to Images conversion with non-PPTX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a PPTX")
        output_path = temp_output_dir / "output"

        with pytest.raises(ConversionError, match="Failed to load PowerPoint file"):
            convert_pptx_to_images(text_file, output_path)

    def test_progress_tracking(self, test_pptx_path, temp_output_dir, mock_python_pptx):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.pptx.to_images.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.pptx.to_images.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.pptx.to_images.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_paths = convert_pptx_to_images(test_pptx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            # Check that complete_operation was called with correct structure
            mock_complete.assert_called_once()
            call_args = mock_complete.call_args
            assert call_args[0][0] == "test_operation_id"
            metadata = call_args[0][1]
            assert "output_path" in metadata
            assert "files" in metadata
            assert isinstance(metadata["files"], list)
            assert len(metadata["files"]) > 0

    def test_event_publishing(self, test_pptx_path, temp_output_dir, mock_python_pptx):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output"

        with patch(
            "transmutation_codex.plugins.pptx.to_images.publish"
        ) as mock_publish:
            result_paths = convert_pptx_to_images(test_pptx_path, output_path)

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
        pptx_to_images_converters = registry.get_plugins_for_conversion(
            "pptx", "images"
        )
        assert len(pptx_to_images_converters) >= 1
