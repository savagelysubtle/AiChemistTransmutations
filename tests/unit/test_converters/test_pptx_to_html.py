"""Tests for PPTX to HTML conversion."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.core.exceptions import ConversionError, ValidationError
from transmutation_codex.plugins.pptx.to_html import convert_pptx_to_html


class TestPPTXToHTMLConverter:
    """Test the PPTX to HTML converter."""

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
            "transmutation_codex.plugins.pptx.to_html.Presentation"
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

    def test_convert_pptx_to_html_basic(
        self, test_pptx_path, temp_output_dir, mock_python_pptx
    ):
        """Test basic PPTX to HTML conversion."""
        output_path = temp_output_dir / "test_output.html"

        result_path = convert_pptx_to_html(test_pptx_path, output_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path == output_path

        # Verify HTML content
        content = result_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "<html lang='en'>" in content
        assert "<head>" in content
        assert "<body>" in content

    def test_convert_pptx_to_html_auto_output(
        self, test_pptx_path, temp_output_dir, mock_python_pptx
    ):
        """Test PPTX to HTML conversion with auto-generated output path."""
        import os

        os.chdir(temp_output_dir)

        result_path = convert_pptx_to_html(test_pptx_path)

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"
        assert result_path.name == "electron_test.html"

    def test_convert_pptx_to_html_custom_options(
        self, test_pptx_path, temp_output_dir, mock_python_pptx
    ):
        """Test PPTX to HTML conversion with custom options."""
        output_path = temp_output_dir / "test_output.html"

        custom_options = {
            "css_styles": "body { font-size: 14px; color: #333; }",
            "slide_range": "1-3",
            "include_notes": False,
            "title": "Custom Title",
        }

        result_path = convert_pptx_to_html(
            test_pptx_path, output_path, **custom_options
        )

        # Verify output
        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify custom options were applied
        content = result_path.read_text(encoding="utf-8")
        assert "font-size: 14px" in content
        assert "Custom Title" in content

    def test_convert_pptx_to_html_invalid_file(self, temp_output_dir):
        """Test PPTX to HTML conversion with invalid file."""
        invalid_path = temp_output_dir / "nonexistent.pptx"
        output_path = temp_output_dir / "output.html"

        with pytest.raises(ValidationError):
            convert_pptx_to_html(invalid_path, output_path)

    def test_convert_pptx_to_html_non_pptx_file(self, temp_output_dir):
        """Test PPTX to HTML conversion with non-PPTX file."""
        # Create a text file
        text_file = temp_output_dir / "test.txt"
        text_file.write_text("This is not a PPTX")
        output_path = temp_output_dir / "output.html"

        with pytest.raises(ConversionError, match="Conversion failed"):
            convert_pptx_to_html(text_file, output_path)

    def test_progress_tracking(self, test_pptx_path, temp_output_dir, mock_python_pptx):
        """Test that progress tracking works correctly."""
        output_path = temp_output_dir / "test_output.html"

        # Mock progress tracking
        with (
            patch(
                "transmutation_codex.plugins.pptx.to_html.start_operation"
            ) as mock_start,
            patch(
                "transmutation_codex.plugins.pptx.to_html.update_progress"
            ) as mock_update,
            patch(
                "transmutation_codex.plugins.pptx.to_html.complete_operation"
            ) as mock_complete,
        ):
            mock_start.return_value = "test_operation_id"

            result_path = convert_pptx_to_html(test_pptx_path, output_path)

            # Verify progress tracking was called
            mock_start.assert_called_once()
            assert mock_update.call_count > 0
            # Check that complete_operation was called with correct structure
            mock_complete.assert_called_once()
            call_args = mock_complete.call_args
            assert call_args[0][0] == "test_operation_id"
            metadata = call_args[0][1]
            assert "output_path" in metadata
            assert "slides_count" in metadata
            assert metadata["slides_count"] == 1

    def test_event_publishing(self, test_pptx_path, temp_output_dir, mock_python_pptx):
        """Test that conversion events are published."""
        output_path = temp_output_dir / "test_output.html"

        with patch("transmutation_codex.plugins.pptx.to_html.publish") as mock_publish:
            result_path = convert_pptx_to_html(test_pptx_path, output_path)

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
        pptx_to_html_converters = registry.get_plugins_for_conversion("pptx", "html")
        assert len(pptx_to_html_converters) >= 1
