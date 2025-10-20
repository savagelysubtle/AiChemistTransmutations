"""Integration tests for the Electron bridge with Phase 1/2 architecture."""

import json
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from transmutation_codex.adapters.bridges.argument_parser import parse_legacy_arguments
from transmutation_codex.adapters.bridges.conversion_handler import handle_conversion
from transmutation_codex.adapters.bridges.electron_bridge import main as bridge_main


class TestElectronBridgeIntegration:
    """Test the Electron bridge integration with new architecture."""

    @pytest.fixture
    def test_pdf_path(self):
        """Path to test PDF file."""
        return Path(__file__).parent.parent / "test_files" / "electron_test.pdf"

    @pytest.fixture
    def test_md_path(self):
        """Path to test Markdown file."""
        return Path(__file__).parent.parent / "test_files" / "electron_test.md"

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield Path(tmpdirname)

    def test_argument_parsing_legacy(self):
        """Test legacy argument parsing."""
        args = [
            "pdf2md",
            "--input-files", "test.pdf",
            "--output", "test.md"
        ]
        
        parsed_args = parse_legacy_arguments(args)
        
        assert parsed_args.mode == "convert"
        assert parsed_args.conversion_type == "pdf2md"
        assert parsed_args.input_path == "test.pdf"
        assert parsed_args.output_path == "test.md"

    def test_argument_parsing_batch(self):
        """Test batch argument parsing."""
        args = [
            "pdf2md",
            "--input-files", "file1.pdf", "file2.pdf",
            "--output-dir", "output/"
        ]
        
        parsed_args = parse_legacy_arguments(args)
        
        assert parsed_args.mode == "batch"
        assert parsed_args.conversion_type == "pdf2md"
        assert parsed_args.input_files == ["file1.pdf", "file2.pdf"]
        assert parsed_args.output_dir == "output/"

    def test_argument_parsing_merge(self):
        """Test merge argument parsing."""
        args = [
            "merge_to_pdf",
            "--input-files", "file1.pdf", "file2.pdf",
            "--output", "merged.pdf"
        ]
        
        parsed_args = parse_legacy_arguments(args)
        
        assert parsed_args.mode == "merge"
        assert parsed_args.conversion_type == "merge_to_pdf"
        assert parsed_args.input_files == ["file1.pdf", "file2.pdf"]
        assert parsed_args.output_path == "merged.pdf"

    def test_conversion_handler_single(self, test_pdf_path, temp_output_dir):
        """Test single file conversion through handler."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock the bridge arguments
        class MockArgs:
            mode = "convert"
            conversion_type = "pdf2md"
            input_path = str(test_pdf_path)
            output_path = str(output_path)
            input_files = None
            output_dir = None
            options = {}
        
        args = MockArgs()
        
        # Mock the conversion
        with patch("transmutation_codex.adapters.bridges.conversion_handler.handle_single_conversion") as mock_convert:
            mock_convert.return_value = str(output_path)
            
            result = handle_conversion(args)
            
            # Verify conversion was called
            mock_convert.assert_called_once_with(args)
            assert result == str(output_path)

    def test_conversion_handler_batch(self, test_pdf_path, temp_output_dir):
        """Test batch conversion through handler."""
        # Mock the bridge arguments
        class MockArgs:
            mode = "batch"
            conversion_type = "pdf2md"
            input_path = None
            output_path = None
            input_files = [str(test_pdf_path)]
            output_dir = str(temp_output_dir)
            options = {}
        
        args = MockArgs()
        
        # Mock the batch conversion
        with patch("transmutation_codex.adapters.bridges.conversion_handler.handle_batch_conversion") as mock_batch:
            mock_batch.return_value = [str(temp_output_dir / "electron_test.md")]
            
            result = handle_conversion(args)
            
            # Verify batch conversion was called
            mock_batch.assert_called_once_with(args)
            assert isinstance(result, list)

    def test_electron_bridge_main(self, test_pdf_path, temp_output_dir):
        """Test the main Electron bridge function."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path)
        ]):
            # Mock the conversion handler
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.return_value = str(output_path)
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit") as mock_exit:
                    bridge_main()
                    
                    # Verify handler was called
                    mock_handler.assert_called_once()
                    # Verify exit was called with success code
                    mock_exit.assert_called_once_with(0)

    def test_electron_bridge_error_handling(self, temp_output_dir):
        """Test Electron bridge error handling."""
        invalid_path = temp_output_dir / "nonexistent.pdf"
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv with invalid file
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(invalid_path),
            "--output", str(output_path)
        ]):
            # Mock the conversion handler to raise an error
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.side_effect = FileNotFoundError("File not found")
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit") as mock_exit:
                    bridge_main()
                    
                    # Verify exit was called with error code
                    mock_exit.assert_called_once_with(1)

    def test_bridge_stdout_output(self, test_pdf_path, temp_output_dir):
        """Test that bridge outputs to stdout correctly."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path)
        ]):
            # Mock the conversion handler
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.return_value = str(output_path)
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit"):
                    # Capture stdout
                    with patch("sys.stdout") as mock_stdout:
                        bridge_main()
                        
                        # Verify stdout was written to
                        mock_stdout.write.assert_called()

    def test_bridge_stderr_output(self, temp_output_dir):
        """Test that bridge outputs errors to stderr correctly."""
        invalid_path = temp_output_dir / "nonexistent.pdf"
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv with invalid file
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(invalid_path),
            "--output", str(output_path)
        ]):
            # Mock the conversion handler to raise an error
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.side_effect = FileNotFoundError("File not found")
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit"):
                    # Capture stderr
                    with patch("sys.stderr") as mock_stderr:
                        bridge_main()
                        
                        # Verify stderr was written to
                        mock_stderr.write.assert_called()

    def test_bridge_json_output(self, test_pdf_path, temp_output_dir):
        """Test that bridge outputs JSON messages correctly."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path)
        ]):
            # Mock the conversion handler
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.return_value = str(output_path)
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit"):
                    # Capture stdout
                    with patch("sys.stdout") as mock_stdout:
                        bridge_main()
                        
                        # Verify JSON output
                        calls = mock_stdout.write.call_args_list
                        json_found = False
                        for call in calls:
                            if call[0][0].startswith("RESULT:"):
                                json_found = True
                                break
                        assert json_found

    def test_bridge_progress_output(self, test_pdf_path, temp_output_dir):
        """Test that bridge outputs progress messages correctly."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path)
        ]):
            # Mock the conversion handler
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.return_value = str(output_path)
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit"):
                    # Capture stdout
                    with patch("sys.stdout") as mock_stdout:
                        bridge_main()
                        
                        # Verify progress output
                        calls = mock_stdout.write.call_args_list
                        progress_found = False
                        for call in calls:
                            if call[0][0].startswith("PROGRESS:"):
                                progress_found = True
                                break
                        assert progress_found

    def test_bridge_subprocess_integration(self, test_pdf_path, temp_output_dir):
        """Test bridge integration through subprocess."""
        output_path = temp_output_dir / "test_output.md"
        
        # Run bridge as subprocess
        cmd = [
            "python", "-m", "transmutation_codex.adapters.bridges.electron_bridge",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent.parent),
                timeout=30
            )
            
            # Verify subprocess completed
            assert result.returncode == 0
            
            # Verify output file was created
            assert output_path.exists()
            
            # Verify stdout contains expected messages
            assert "PROGRESS:" in result.stdout
            assert "RESULT:" in result.stdout
            
        except subprocess.TimeoutExpired:
            pytest.skip("Subprocess test timed out")

    def test_bridge_error_subprocess(self, temp_output_dir):
        """Test bridge error handling through subprocess."""
        invalid_path = temp_output_dir / "nonexistent.pdf"
        output_path = temp_output_dir / "test_output.md"
        
        # Run bridge as subprocess with invalid file
        cmd = [
            "python", "-m", "transmutation_codex.adapters.bridges.electron_bridge",
            "pdf2md",
            "--input-files", str(invalid_path),
            "--output", str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent.parent.parent),
                timeout=30
            )
            
            # Verify subprocess failed
            assert result.returncode == 1
            
            # Verify stderr contains error message
            assert "ERROR:" in result.stderr
            
        except subprocess.TimeoutExpired:
            pytest.skip("Subprocess test timed out")

    def test_bridge_converter_selection(self, test_pdf_path, temp_output_dir):
        """Test that bridge selects the correct converter."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path)
        ]):
            # Mock the registry to verify converter selection
            with patch("transmutation_codex.adapters.bridges.conversion_handler.get_registry") as mock_registry:
                mock_registry.return_value.get_best_converter.return_value = Mock(
                    name="test_converter",
                    priority=10
                )
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit"):
                    bridge_main()
                    
                    # Verify registry was used to get converter
                    mock_registry.return_value.get_best_converter.assert_called_with("pdf", "md")

    def test_bridge_options_passing(self, test_pdf_path, temp_output_dir):
        """Test that bridge passes options correctly to converters."""
        output_path = temp_output_dir / "test_output.md"
        
        # Mock sys.argv with options
        with patch("sys.argv", [
            "electron_bridge.py",
            "pdf2md",
            "--input-files", str(test_pdf_path),
            "--output", str(output_path),
            "--engine", "basic",
            "--lang", "eng"
        ]):
            # Mock the conversion handler
            with patch("transmutation_codex.adapters.bridges.electron_bridge.handle_conversion") as mock_handler:
                mock_handler.return_value = str(output_path)
                
                # Mock sys.exit to prevent actual exit
                with patch("sys.exit"):
                    bridge_main()
                    
                    # Verify handler was called with options
                    args = mock_handler.call_args[0][0]
                    assert args.options["engine"] == "basic"
                    assert args.options["lang"] == "eng"