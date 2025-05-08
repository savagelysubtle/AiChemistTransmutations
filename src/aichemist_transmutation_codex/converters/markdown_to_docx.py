import logging
import os
import platform
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Try to import pypandoc, which is a Python wrapper for Pandoc.
# Pandoc is a powerful command-line tool for document conversion.
try:
    import pypandoc
except ImportError as e:
    # If pypandoc is not installed, we'll raise an informative error later
    # when the conversion function is actually called.
    # This allows the module to be imported even if pypandoc is missing,
    # and the error will only occur if a conversion is attempted.
    pypandoc = None  # Set to None to check its availability later
    _pypandoc_import_error = e


# Configure logging
logger = logging.getLogger(__name__)


def get_pandoc_path() -> str:
    """
    Attempts to find the path to the pandoc executable.
    Checks common installation locations and the system PATH.
    Raises FileNotFoundError if pandoc is not found.
    """
    # Common locations for pandoc
    common_paths = []
    if platform.system() == "Windows":
        # Using raw strings (r"...") for default paths to avoid issues with backslashes.
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get(
            "ProgramFiles(x86)", r"C:\Program Files (x86)"
        )
        local_app_data = os.environ.get(
            "LOCALAPPDATA",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local"),
        )

        common_paths.extend(
            [
                os.path.join(program_files, "Pandoc", "pandoc.exe"),
                os.path.join(program_files_x86, "Pandoc", "pandoc.exe"),
                os.path.join(local_app_data, "Pandoc", "pandoc.exe"),
            ]
        )
    elif platform.system() == "Linux":
        common_paths.extend(
            [
                "/usr/bin/pandoc",
                "/usr/local/bin/pandoc",
                os.path.expanduser("~/.local/bin/pandoc"),
            ]
        )
    elif platform.system() == "Darwin":  # macOS
        common_paths.extend(
            [
                "/usr/local/bin/pandoc",
                "/opt/homebrew/bin/pandoc",  # Apple Silicon Homebrew
            ]
        )

    for path in common_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            logger.info(f"Found pandoc at: {path}")
            return path

    # Check PATH if not found in common locations
    try:
        # Use `where` on Windows, `which` on Unix-like systems
        cmd = (
            ["where", "pandoc"]
            if platform.system() == "Windows"
            else ["which", "pandoc"]
        )
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        pandoc_path = result.stdout.strip().splitlines()[
            0
        ]  # Take the first result if multiple
        if os.path.exists(pandoc_path) and os.access(pandoc_path, os.X_OK):
            logger.info(f"Found pandoc in PATH: {pandoc_path}")
            return pandoc_path
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError) as e:
        logger.warning(f"Pandoc not found in PATH: {e}")
        pass  # Continue to raise FileNotFoundError if not found

    logger.error("Pandoc executable not found in common locations or PATH.")
    raise FileNotFoundError(
        "Pandoc executable not found. Please ensure pandoc is installed and in your PATH."
    )


def markdown_to_docx(
    input_path: str | Path,
    output_path: str | Path | None = None,
    reference_docx: str | Path | None = None,
    **kwargs: Any,
) -> Path:
    """
    Converts a Markdown file to a DOCX document using pypandoc.

    Args:
        input_path: Path to the input Markdown file (as str or Path).
        output_path: Path to save the output DOCX file (as str or Path).
                     If None, a default name might be generated or an error raised.
                     (Current implementation requires it, this change is for signature compatibility)
        reference_docx: Path to a reference DOCX file (as str or Path).
        **kwargs: Additional keyword arguments. Expects 'progress_callback'.

    Returns:
        Path object of the generated DOCX file.

    Raises:
        FileNotFoundError: If the input Markdown file is not found or Pandoc is not found.
        RuntimeError: If Pandoc conversion fails or output_path is None and not handled.
        ValueError: If output_path is None (as current implementation requires it).
    """
    progress_callback: Callable[[int, str], None] | None = kwargs.get(
        "progress_callback"
    )

    if output_path is None:
        # Current implementation requires an output path.
        # For a more robust solution, you might generate a default output path here
        # or clearly document that it's required despite the optional signature.
        err_msg = "output_path cannot be None for markdown_to_docx conversion."
        logger.error(err_msg)
        raise ValueError(err_msg)

    input_markdown_path_str = str(input_path)
    output_docx_path_str = str(output_path)

    logger.info(
        f"Starting Markdown to DOCX conversion: {input_markdown_path_str} -> {output_docx_path_str}"
    )

    if not os.path.exists(input_markdown_path_str):
        logger.error(f"Input Markdown file not found: {input_markdown_path_str}")
        raise FileNotFoundError(
            f"Input Markdown file not found: {input_markdown_path_str}"
        )

    # Ensure output directory exists
    output_dir = os.path.dirname(output_docx_path_str)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    if progress_callback:
        progress_callback(0, "Initializing Pandoc...")

    try:
        # Set PANDOC_PATH environment variable for pypandoc
        # This is crucial if pypandoc doesn't find it automatically, especially in packaged apps
        original_pandoc_env = os.environ.get("PANDOC_PATH")
        try:
            pandoc_executable_path = get_pandoc_path()
            os.environ["PANDOC_PATH"] = pandoc_executable_path
            logger.info(f"Temporarily set PANDOC_PATH to: {pandoc_executable_path}")
        except FileNotFoundError as e:
            logger.error(f"Pandoc not found: {e}. Cannot proceed with conversion.")
            raise

        if progress_callback:
            progress_callback(20, "Pandoc initialized. Starting conversion...")

        # pypandoc.convert_file can sometimes have issues with complex paths or finding pandoc.
        # Using pypandoc.ensure_pandoc_path can help, but explicitly setting ENV is more robust.
        # The 'format' argument specifies the input format (Markdown in this case).
        # The 'to' argument specifies the output format (DOCX).
        # The 'outputfile' argument specifies where to save the converted document.
        # 'extra_args' can be used to pass additional Pandoc command-line options.
        pypandoc.convert_file(
            input_markdown_path_str,
            to="docx",
            format="markdown",
            outputfile=output_docx_path_str,
            extra_args=["--standalone"],
        )

        if progress_callback:
            progress_callback(100, "Conversion successful.")
        logger.info(
            f"Successfully converted {input_markdown_path_str} to {output_docx_path_str}"
        )
        return Path(output_docx_path_str)

    except FileNotFoundError:
        # No need to log again, already logged in get_pandoc_path
        raise
    except Exception as e:  # Catches pypandoc.PandocError or other runtime issues
        error_message = f"Pandoc conversion failed: {e}"
        logger.error(error_message)
        if progress_callback:
            progress_callback(-1, f"Error: {error_message}")
        # Attempt to get more detailed error output from Pandoc if pypandoc allows
        # This might require direct subprocess call if pypandoc.PandocError doesn't have enough info
        raise RuntimeError(error_message) from e
    finally:
        # Restore original PANDOC_PATH if it was set
        if original_pandoc_env is None:
            if "PANDOC_PATH" in os.environ:
                del os.environ["PANDOC_PATH"]
                logger.info("Restored PANDOC_PATH: unset.")
        else:
            os.environ["PANDOC_PATH"] = original_pandoc_env
            logger.info(f"Restored PANDOC_PATH to: {original_pandoc_env}")


if __name__ == "__main__":
    # Basic example for testing the converter directly
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Create dummy files for testing
    test_md_content = """
# Markdown to DOCX Test

This is a test document for converting Markdown to DOCX using Pandoc.

- Item 1
- Item 2

**Bold text** and *italic text*.

```python
print("Hello, Pandoc!")
```
    """
    test_md_file = Path("test_input.md")
    output_docx_file = Path("test_output.docx")

    with open(test_md_file, "w", encoding="utf-8") as f:
        f.write(test_md_content)

    def sample_progress_callback(percentage: int, message: str):
        print(f"Progress: {percentage}% - {message}")

    try:
        print(
            f"Attempting to convert {str(test_md_file)} to {str(output_docx_file)}..."
        )
        # Attempt to find pandoc before conversion (optional, but good for pre-check)
        try:
            print(f"Pandoc found at: {get_pandoc_path()}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print(
                "Please ensure Pandoc is installed and in your system PATH or common locations."
            )
            exit(1)

        # Pass progress_callback via kwargs for testing
        converted_file_path = markdown_to_docx(
            test_md_file, output_docx_file, progress_callback=sample_progress_callback
        )
        print(f"Conversion successful! Output file: {str(converted_file_path)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(
            "Please ensure Pandoc is installed and in your system PATH or common locations."
        )
    except RuntimeError as e:
        print(f"Runtime error during conversion: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Clean up dummy files
        if os.path.exists(test_md_file):
            os.remove(test_md_file)
        # if os.path.exists(output_docx_file): # Keep output for inspection
        #     os.remove(output_docx_file)
        pass
