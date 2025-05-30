"""Unit tests for the batch processor module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from mdtopdf.batch_processor import run_batch


@pytest.fixture
def mock_converter():
    """Create a mock converter function."""

    def _converter(input_path, output_path=None, **kwargs):
        if output_path is None:
            output_path = Path(input_path).with_suffix(".out")
        return Path(output_path)

    return Mock(side_effect=_converter)


@pytest.fixture
def temp_files():
    """Create temporary test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        files = []
        for i in range(3):
            path = Path(tmpdir) / f"test{i}.txt"
            path.write_text(f"Test content {i}")
            files.append(path)
        yield files


def test_run_batch_basic(mock_converter, temp_files):
    """Test basic batch processing functionality."""
    with patch("mdtopdf.batch_processor.importlib.import_module") as mock_import:
        # Configure mock module
        mock_module = Mock()
        mock_module.convert_pdf_to_md = mock_converter
        mock_import.return_value = mock_module

        # Run batch conversion
        result = run_batch(
            conversion_type="pdf2md", input_files=temp_files, max_workers=2
        )

        # Verify results
        assert result["total_files"] == len(temp_files)
        assert result["successful"] == len(temp_files)
        assert result["failed"] == 0
        assert len(result["results"]) == len(temp_files)
        assert all(r["success"] for r in result["results"])


def test_run_batch_with_failures(mock_converter, temp_files):
    """Test batch processing with some failures."""

    def failing_converter(input_path, **kwargs):
        if "test1" in str(input_path):
            raise ValueError("Simulated failure")
        return Path(input_path).with_suffix(".out")

    with patch("mdtopdf.batch_processor.importlib.import_module") as mock_import:
        # Configure mock module with failing converter
        mock_module = Mock()
        # Create a mock converter class and instance
        mock_converter_class = Mock()
        mock_converter_instance = Mock()
        # Set the convert method on the instance to use our failing converter
        mock_converter_instance.convert = Mock(side_effect=failing_converter)
        # Make the class return our instance when instantiated
        mock_converter_class.return_value = mock_converter_instance
        # Set the class on the module
        mock_module.PDFToMarkdownConverter = mock_converter_class
        mock_import.return_value = mock_module

        # Run batch conversion
        result = run_batch(
            conversion_type="pdf2md", input_files=temp_files, max_workers=2
        )

        # Verify results
        assert result["total_files"] == len(temp_files)
        assert result["successful"] == len(temp_files) - 1
        assert result["failed"] == 1
        assert len(result["results"]) == len(temp_files)
        assert any(not r["success"] for r in result["results"])


def test_run_batch_with_progress_callback(mock_converter, temp_files):
    """Test batch processing with progress callback."""
    progress_callback = Mock()

    with patch("mdtopdf.batch_processor.importlib.import_module") as mock_import:
        # Configure mock module
        mock_module = Mock()
        mock_module.convert_pdf_to_md = mock_converter
        mock_import.return_value = mock_module

        # Run batch conversion
        result = run_batch(
            conversion_type="pdf2md",
            input_files=temp_files,
            max_workers=2,
            progress_callback=progress_callback,
        )

        # Verify callback was called for each file
        assert progress_callback.call_count == len(temp_files)
        # Verify callback arguments
        for i, call in enumerate(progress_callback.call_args_list, 1):
            args = call[0]
            assert args[0] == i  # file index
            assert args[1] == len(temp_files)  # total files
            assert isinstance(args[2], str)  # input path
            assert isinstance(args[3], bool)  # success status
            assert isinstance(args[4], float)  # processing time
            assert args[5] is None  # error message (None for success)


def test_run_batch_invalid_conversion_type():
    """Test batch processing with invalid conversion type."""
    with pytest.raises(ValueError, match="Unsupported conversion type"):
        run_batch(
            conversion_type="invalid", input_files=[Path("test.txt")], max_workers=1
        )


def test_run_batch_with_output_dir(mock_converter, temp_files):
    """Test batch processing with custom output directory."""
    with tempfile.TemporaryDirectory() as output_dir:
        with patch("mdtopdf.batch_processor.importlib.import_module") as mock_import:
            # Configure mock module
            mock_module = Mock()
            mock_module.convert_pdf_to_md = mock_converter
            mock_import.return_value = mock_module

            # Run batch conversion
            result = run_batch(
                conversion_type="pdf2md",
                input_files=temp_files,
                output_dir=output_dir,
                max_workers=2,
            )

            # Verify results
            assert result["successful"] == len(temp_files)
            # Verify output directory was created and used
            assert os.path.exists(output_dir)
            assert all("output_path" in r for r in result["results"])


def test_run_batch_with_converter_options(mock_converter, temp_files):
    """Test batch processing with additional converter options."""
    test_options = {"lang": "eng", "dpi": 300}

    with patch("mdtopdf.batch_processor.importlib.import_module") as mock_import:
        # Configure mock module
        mock_module = Mock()
        mock_module.convert_pdf_to_md = mock_converter
        mock_import.return_value = mock_module

        # Run batch conversion
        result = run_batch(
            conversion_type="pdf2md",
            input_files=temp_files,
            max_workers=2,
            **test_options,
        )

        # Verify converter was called with options
        for call in mock_converter.call_args_list:
            _, kwargs = call
            assert all(item in kwargs.items() for item in test_options.items())
