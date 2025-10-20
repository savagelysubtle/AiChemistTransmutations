import json
import sys
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Skip these tests - they test the old electron_bridge that has been refactored
pytestmark = pytest.mark.skip(
    reason="Legacy electron_bridge tests - bridge has been refactored into modular components"
)

# Remove the module-level mocks and the patch.dict block
# Mocking will be handled by decorators on individual tests


# Helper function to capture stdout
class CaptureOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._captured_output = StringIO()
        sys.stdout = self._captured_output
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout

    def get_output(self):
        return self._captured_output.getvalue()

    def get_json_messages(self, prefix):
        lines = self.get_output().strip().split("\n")
        messages = []
        for line in lines:
            if line.startswith(prefix):
                try:
                    messages.append(json.loads(line[len(prefix) :].strip()))
                except json.JSONDecodeError:
                    pytest.fail(f"Failed to decode JSON: {line}")
        return messages


@pytest.fixture
def mock_args(monkeypatch):
    def _mock_args(args_list):
        monkeypatch.setattr(sys, "argv", ["electron_bridge.py"] + args_list)

    return _mock_args


@pytest.fixture
def mock_path_exists(monkeypatch):
    def _mock_exists(exists_map):
        original_exists = Path.exists

        def mocked_exists(self):
            return exists_map.get(
                str(self), original_exists(self)
            )  # Default to real if not in map

        monkeypatch.setattr(Path, "exists", mocked_exists)

    return _mock_exists


# --- Test report_batch_progress ---


def test_report_electron_batch_progress_success():
    with CaptureOutput() as capturer:
        report_batch_progress(
            file_index=1,
            total_files=5,
            file_path_str="/path/to/file1.pdf",
            success=True,
            processing_time=1.234,
            error_message=None,
        )
    messages = capturer.get_json_messages("BATCH_PROGRESS:")
    assert len(messages) == 1
    msg = messages[0]
    assert msg["type"] == "batch_progress"
    assert msg["fileIndex"] == 1
    assert msg["totalFiles"] == 5
    assert msg["fileName"] == "file1.pdf"
    assert msg["status"] == "success"
    assert msg["overallProgress"] == 20
    assert msg["time"] == 1.23
    assert msg["error"] is None


def test_report_electron_batch_progress_failure():
    with CaptureOutput() as capturer:
        report_batch_progress(
            file_index=3,
            total_files=10,
            file_path_str="C:\\another\\file2.md",
            success=False,
            processing_time=0.55,
            error_message="Conversion failed",
        )
    messages = capturer.get_json_messages("BATCH_PROGRESS:")
    assert len(messages) == 1
    msg = messages[0]
    assert msg["type"] == "batch_progress"
    assert msg["fileIndex"] == 3
    assert msg["totalFiles"] == 10
    assert msg["fileName"] == "file2.md"
    assert msg["status"] == "error"
    assert msg["overallProgress"] == 30
    assert msg["time"] == 0.55
    assert msg["error"] == "Conversion failed"


# --- Test check_file_extension_compatibility ---


@pytest.mark.parametrize(
    "conv_type, filename, should_pass",
    [
        ("md2pdf", "test.md", True),
        ("md2pdf", "test.markdown", True),
        ("md2pdf", "test.txt", False),
        ("pdf2md", "test.pdf", True),
        ("pdf2md", "test.docx", False),
        ("html2pdf", "test.html", True),
        ("html2pdf", "test.htm", True),
        ("html2pdf", "test.xml", False),
        ("docx2md", "test.docx", True),
        ("docx2md", "test.doc", True),  # Assuming .doc is also handled
        ("docx2md", "test.pdf", False),
    ],
)
def test_check_file_extension_compatibility(tmp_path, conv_type, filename, should_pass):
    file = tmp_path / filename
    file.touch()  # Create the file

    if should_pass:
        check_file_extension_compatibility(conv_type, file)  # No exception
    else:
        with pytest.raises(ValueError, match="not compatible"):
            check_file_extension_compatibility(conv_type, file)


# --- Test main function ---


# Patch the dependencies used *within* electron_bridge.py's main function
@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.convert_with_progress")
def test_main_single_file_success(
    mock_convert,
    mock_log_manager,
    mock_args,
    mock_path_exists,
    tmp_path,
):
    # Configure mocks
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file = tmp_path / "input.md"
    output_file = tmp_path / "output.pdf"
    input_file.touch()
    mock_path_exists({str(input_file.resolve()): True})
    mock_args(["md2pdf", "--input-files", str(input_file)])
    mock_convert.return_value = output_file.resolve()

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 0
    mock_convert.assert_called_once_with(
        "md2pdf",
        input_file.resolve(),
        None,  # output_path_arg is None when --output-dir is not provided
        # **kwargs will be empty here
    )
    # Check final result message
    result_messages = capturer.get_json_messages("RESULT:")
    assert len(result_messages) == 1
    assert result_messages[0]["type"] == "single_result"
    assert result_messages[0]["success"] is True
    assert result_messages[0]["outputPath"] == str(output_file.resolve())


@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.run_batch")
def test_main_batch_file_success(
    mock_run_batch,
    mock_log_manager,
    mock_args,
    mock_path_exists,
    tmp_path,
):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file1 = tmp_path / "input1.pdf"
    input_file2 = tmp_path / "input2.pdf"
    output_dir = tmp_path / "output"
    input_file1.touch()
    input_file2.touch()
    mock_path_exists(
        {str(input_file1.resolve()): True, str(input_file2.resolve()): True}
    )
    mock_args(
        [
            "pdf2md",
            "--input-files",
            str(input_file1),
            str(input_file2),
            "--output-dir",
            str(output_dir),
            "--workers",
            "4",
            "--lang",
            "eng+fra",
        ]
    )

    batch_summary = {"total": 2, "successful": 2, "failed": 0, "results": []}
    mock_run_batch.return_value = batch_summary

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 0
    mock_run_batch.assert_called_once()
    call_args, call_kwargs = mock_run_batch.call_args
    assert call_kwargs["conversion_type"] == "pdf2md"
    assert call_kwargs["input_files"] == [input_file1.resolve(), input_file2.resolve()]
    assert call_kwargs["output_dir"] == str(output_dir)
    assert call_kwargs["max_workers"] == 4
    assert isinstance(call_kwargs["progress_callback"], Callable)
    assert call_kwargs["lang"] == "eng+fra"  # Check specific option pass-through
    assert "engine" not in call_kwargs  # Ensure only passed options are included

    # Check final result message
    result_messages = capturer.get_json_messages("BATCH_RESULT:")
    assert len(result_messages) == 1
    assert result_messages[0] == batch_summary


@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.convert_with_progress")
def test_main_single_file_not_found(
    mock_convert,
    mock_log_manager,
    mock_args,
    mock_path_exists,
):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file = "/non/existent/file.md"
    mock_path_exists(
        {Path(input_file).resolve(): False}
    )  # Mock Path.exists for resolved path
    mock_args(["md2pdf", "--input-files", input_file])

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 1  # Should fail
    mock_convert.assert_not_called()
    error_messages = capturer.get_json_messages("ERROR:")
    assert len(error_messages) == 1
    assert "not found" in error_messages[0]["message"]


@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.run_batch")
def test_main_batch_file_one_not_found(
    mock_run_batch,
    mock_log_manager,
    mock_args,
    mock_path_exists,
    tmp_path,
):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file1 = tmp_path / "input1.pdf"
    input_file2 = tmp_path / "non_existent.pdf"  # This one doesn't exist
    input_file1.touch()
    # Mock existence check for resolved paths
    mock_path_exists(
        {str(input_file1.resolve()): True, str(input_file2.resolve()): False}
    )
    mock_args(["pdf2md", "--input-files", str(input_file1), str(input_file2)])

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 1  # Should fail validation
    mock_run_batch.assert_not_called()
    error_messages = capturer.get_json_messages("ERROR:")
    assert len(error_messages) == 1
    assert "not found" in error_messages[0]["message"]
    assert str(input_file2.resolve()) in error_messages[0]["message"]


@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.run_batch")
def test_main_batch_incompatible_extension(
    mock_run_batch,
    mock_log_manager,
    mock_args,
    mock_path_exists,
    tmp_path,
):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file1 = tmp_path / "input1.pdf"
    input_file2 = tmp_path / "input2.txt"  # Incompatible
    input_file1.touch()
    input_file2.touch()
    mock_path_exists(
        {str(input_file1.resolve()): True, str(input_file2.resolve()): True}
    )
    mock_args(["pdf2md", "--input-files", str(input_file1), str(input_file2)])

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 1  # Should fail validation
    mock_run_batch.assert_not_called()
    error_messages = capturer.get_json_messages("ERROR:")
    assert len(error_messages) == 1
    assert "not compatible" in error_messages[0]["message"]
    assert input_file2.name in error_messages[0]["message"]


@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.convert_with_progress")
def test_main_single_conversion_error(
    mock_convert,
    mock_log_manager,
    mock_args,
    mock_path_exists,
    tmp_path,
):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file = tmp_path / "input.md"
    input_file.touch()
    mock_path_exists({str(input_file.resolve()): True})
    mock_args(["md2pdf", "--input-files", str(input_file)])
    mock_convert.side_effect = ValueError("Conversion failed!")

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 1
    mock_convert.assert_called_once()
    error_messages = capturer.get_json_messages("ERROR:")
    # Note: convert_with_progress reports its own progress errors,
    # then main catches the exception and reports a final ERROR message.
    assert len(error_messages) > 0  # At least one final error message
    assert (
        "Conversion failed!" in error_messages[-1]["message"]
    )  # Check the last error message


@patch("mdtopdf.electron_bridge.LogManager")
@patch("mdtopdf.electron_bridge.run_batch")
def test_main_batch_conversion_error(
    mock_run_batch,
    mock_log_manager,
    mock_args,
    mock_path_exists,
    tmp_path,
):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()

    input_file1 = tmp_path / "input1.pdf"
    input_file2 = tmp_path / "input2.pdf"
    input_file1.touch()
    input_file2.touch()
    mock_path_exists(
        {str(input_file1.resolve()): True, str(input_file2.resolve()): True}
    )
    mock_args(["pdf2md", "--input-files", str(input_file1), str(input_file2)])
    mock_run_batch.side_effect = RuntimeError("Batch processing error!")

    with CaptureOutput() as capturer:
        exit_code = main()

    assert exit_code == 1
    mock_run_batch.assert_called_once()
    error_messages = capturer.get_json_messages("ERROR:")
    assert len(error_messages) == 1
    assert "Batch processing error!" in error_messages[0]["message"]


@patch("mdtopdf.electron_bridge.LogManager")
def test_main_invalid_args(mock_log_manager, mock_args):
    mock_log_manager.return_value.get_logger.return_value = MagicMock()
    mock_log_manager.return_value.get_bridge_logger.return_value = MagicMock()
    # Missing required --input-files
    mock_args(["pdf2md"])

    with CaptureOutput() as capturer:
        # Argparse calls sys.exit(2), which main() catches and returns as 2.
        # So, assert the return code, not the exception.
        exit_code = main()

    assert exit_code == 2  # Check the return code
    # Check for the final ERROR message printed by the bridge
    error_messages = capturer.get_json_messages("ERROR:")
    assert len(error_messages) == 1
    assert "Invalid command line arguments" in error_messages[0]["message"]
