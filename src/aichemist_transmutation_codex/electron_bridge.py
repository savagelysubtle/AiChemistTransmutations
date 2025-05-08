#!/usr/bin/env python
"""
Electron Bridge module for MDtoPDF Converter.

Provides interfaces between the converter and an Electron frontend with progress reporting.
"""

import argparse
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

# Resolve the project's src directory and add it to sys.path
# This allows absolute imports of modules within the aichemist_transmutation_codex package
# when electron_bridge.py is run as a script.
# __file__ is .../AichemistTransmutationCodex/src/aichemist_transmutation_codex/electron_bridge.py
# .parent is .../AichemistTransmutationCodex/src/aichemist_transmutation_codex
# .parent.parent (src_path) is .../AichemistTransmutationCodex/src
_src_path = Path(__file__).resolve().parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from aichemist_transmutation_codex.batch_processor import run_batch
from aichemist_transmutation_codex.config import LogManager


def _report_electron_progress(
    current_step: int,
    total_steps: int,
    message: str,
    progress_type: str = "single",
) -> None:
    """Reports single file progress to Electron via stdout.

    Formats the progress data as a JSON string prefixed with "PROGRESS:".

    Args:
        current_step (int): The current step in the process.
        total_steps (int): The total number of steps in the process.
        message (str): A message describing the current state.
        progress_type (str): A string indicating the type of progress report
            (e.g., "single_progress", "single_error", "single_complete").
            Defaults to "single".
    """
    progress = int((current_step / total_steps) * 100) if total_steps > 0 else 0
    progress_data = {
        "type": progress_type,  # e.g., "single_progress"
        "progress": progress,
        "message": message,
    }
    try:
        print(f"PROGRESS: {json.dumps(progress_data)}")
        sys.stdout.flush()
    except Exception as e:
        logger = LogManager().get_bridge_logger()
        logger.error(f"Failed to report progress: {e}")


def _report_electron_batch_progress(
    file_index: int,
    total_files: int,
    file_path_str: str,
    success: bool,
    processing_time: float,
    error_message: str | None,
    # Add shared state for overall progress if needed, e.g., counters
    # successful_count: list[int], # Use list for mutable integer
    # failed_count: list[int],
    # lock: threading.Lock
) -> None:
    """Callback function to report batch processing progress to Electron.

    This function is invoked by the `run_batch` function for each file processed
    in a batch operation. It formats the progress data as a JSON string
    prefixed with "BATCH_PROGRESS:" and prints it to stdout.

    Args:
        file_index (int): The 1-based index of the currently processed file.
        total_files (int): The total number of files in the batch.
        file_path_str (str): The string path of the input file being processed.
        success (bool): True if the file was processed successfully, False otherwise.
        processing_time (float): The time taken to process the file, in seconds.
        error_message (str | None): An error message if processing failed,
            otherwise None.
    """
    # Note: Direct updates to shared counters (successful/failed)
    # should happen outside this callback in the main thread
    # that iterates through batch_processor results for simplicity,
    # OR use locks if updating here.

    status = "success" if success else ("error" if error_message else "failed")
    file_name = Path(file_path_str).name

    # Calculate overall progress based on file index
    overall_progress = min(100, int((file_index / max(1, total_files)) * 100))

    progress_data = {
        "type": "batch_progress",
        "fileIndex": file_index,
        "totalFiles": total_files,
        "fileName": file_name,
        "status": status,
        "overallProgress": overall_progress,
        "time": round(processing_time, 2),
        "error": error_message,
    }
    try:
        print(f"BATCH_PROGRESS: {json.dumps(progress_data)}")
        sys.stdout.flush()
        logger = LogManager().get_bridge_logger()
        logger.debug(
            f"Reported batch progress: File {file_index}/{total_files} - {file_name} ({status})"
        )
    except Exception as e:
        logger = LogManager().get_bridge_logger()
        logger.error(f"Failed to report batch progress for {file_name}: {e}")


def check_file_extension_compatibility(conversion_type: str, input_path: Path) -> None:
    """Checks if the input file's extension is compatible with the conversion type.

    Args:
        conversion_type (str): The target conversion type (e.g., "pdf2md").
        input_path (Path): Path to the input file.

    Raises:
        ValueError: If the file extension is not compatible with the
            specified conversion type.
    """
    # ... (function remains the same, logging handled by caller)
    extension = input_path.suffix.lower()

    compatible = True
    expected = ""

    if conversion_type in ("md2pdf", "md2html"):
        if extension not in (".md", ".markdown"):
            compatible = False
            expected = ".md or .markdown"
    elif conversion_type in ("pdf2html", "pdf2md"):
        if extension != ".pdf":
            compatible = False
            expected = ".pdf"
    elif conversion_type == "html2pdf":
        if extension not in (".html", ".htm"):
            compatible = False
            expected = ".html or .htm"
    elif conversion_type == "docx2md":
        if extension not in (".docx", ".doc"):
            compatible = False
            expected = ".docx or .doc"
    elif conversion_type == "pdf2editable":
        if extension != ".pdf":
            compatible = False
            expected = ".pdf"
    # Add compatibility for md2docx
    elif conversion_type == "md2docx":
        if extension not in (".md", ".markdown"):
            compatible = False
            expected = ".md or .markdown"
    # Add compatibility for docx2pdf
    elif conversion_type == "docx2pdf":
        if extension not in (".docx"):
            compatible = False
            expected = ".docx"

    if not compatible:
        error_msg = f"Input file {input_path.name} is not compatible with {conversion_type} conversion. Expected {expected}."
        logger = LogManager().get_bridge_logger()
        logger.error(error_msg)
        raise ValueError(error_msg)
    else:
        logger = LogManager().get_bridge_logger()
        logger.debug(f"File {input_path.name} compatible with {conversion_type}.")


def convert_with_progress(
    conversion_type: str,
    input_path: str | Path,
    output_path: str | Path | None = None,
    **kwargs: Any,
) -> Path:
    """Converts a single file and reports progress to Electron.

    This function handles the conversion of a single file. It dynamically imports
    the appropriate converter based on `conversion_type`, executes the conversion,
    and reports progress updates (initialization, steps, completion/error) to
    Electron via stdout.

    Args:
        conversion_type (str): The type of conversion (e.g., "pdf2md", "md2pdf").
        input_path (str | Path): The path to the input file.
        output_path (str | Path | None): The desired path for the output file.
            If it's a directory, a filename will be generated based on the input.
            If None, the converter typically saves the output next to the input file
            with an appropriate extension. Defaults to None.
        **kwargs (Any): Additional keyword arguments to be passed to the specific
            converter function.

    Returns:
        Path: The absolute path to the successfully converted output file.

    Raises:
        FileNotFoundError: If `input_path` does not exist.
        ValueError: If `conversion_type` is unknown or if the input file is
            incompatible with the selected conversion.
        ImportError: If the required converter module or its dependencies
            cannot be loaded.
        RuntimeError: For other unexpected errors during the conversion process.
    """
    logger = LogManager().get_bridge_logger()
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Handle case where output_path is a directory
    if output_path is not None:
        output_path = Path(output_path)
        if output_path.is_dir():
            # Create a filename based on the input file, but with correct extension
            if conversion_type == "pdf2md":
                output_path = output_path / input_path.with_suffix(".md").name
            elif conversion_type == "md2pdf":
                output_path = output_path / input_path.with_suffix(".pdf").name
            elif conversion_type == "html2pdf":
                output_path = output_path / input_path.with_suffix(".pdf").name
            elif conversion_type == "md2html":
                output_path = output_path / input_path.with_suffix(".html").name
            elif conversion_type == "pdf2html":
                output_path = output_path / input_path.with_suffix(".html").name
            elif conversion_type == "docx2md":
                output_path = output_path / input_path.with_suffix(".md").name
            elif conversion_type == "pdf2editable":
                output_path = output_path / f"{input_path.stem}_editable.pdf"
            # Add output path generation for md2docx
            elif conversion_type == "md2docx":
                output_path = output_path / input_path.with_suffix(".docx").name
            # Add output path generation for docx2pdf
            elif conversion_type == "docx2pdf":
                output_path = output_path / input_path.with_suffix(".pdf").name
            logger.info(f"Output path is a directory, using file path: {output_path}")

    logger.info(
        f"Starting single file conversion: {conversion_type} for {input_path.name}"
    )
    _report_electron_progress(0, 100, "Initializing...", "single_progress")

    # Check compatibility before importing
    try:
        check_file_extension_compatibility(conversion_type, input_path)
    except ValueError as e:
        _report_electron_progress(100, 100, f"Error: {e}", "single_error")
        raise

    _report_electron_progress(10, 100, "Importing converter...", "single_progress")
    # Import the appropriate converter function or class method
    try:
        # Map conversion type to module and function/method
        conversion_map = {
            "pdf2md": (
                "converters.pdf_to_markdown",
                "PDFToMarkdownConverter",
                "convert",
            ),
            "md2pdf": ("converters.markdown_to_pdf", None, "convert_md_to_pdf"),
            "html2pdf": ("converters.html_to_pdf", None, "convert_html_to_pdf"),
            "md2html": ("converters.markdown_to_html", None, "convert_md_to_html"),
            "pdf2html": ("converters.pdf_to_html", None, "convert_pdf_to_html"),
            "docx2md": ("converters.docx_to_markdown", None, "convert_docx_to_md"),
            "pdf2editable": (
                "converters.pdf_to_editable_pdf",
                None,
                "convert_pdf_to_editable",
            ),
            # Add md2docx to the conversion map
            "md2docx": ("converters.markdown_to_docx", None, "markdown_to_docx"),
            # Add docx2pdf to the conversion map
            "docx2pdf": ("converters.doc_to_pdf", None, "convert_docx_to_pdf"),
        }
        if conversion_type not in conversion_map:
            raise ValueError(f"Unknown conversion type: {conversion_type}")

        module_path, class_name, func_name = conversion_map[conversion_type]
        module = importlib.import_module(
            f".{module_path}", package="aichemist_transmutation_codex"
        )

        if class_name:
            ConverterClass = getattr(module, class_name)
            converter_instance = (
                ConverterClass()
            )  # Assumes constructor doesn't need args here
            converter_callable = getattr(converter_instance, func_name)
        else:
            converter_callable = getattr(module, func_name)

    except (ImportError, AttributeError, ValueError) as e:
        logger.exception(f"Failed to load converter for {conversion_type}: {e}")
        _report_electron_progress(
            100, 100, f"Error: Failed to load converter - {e}", "single_error"
        )
        raise ImportError(f"Failed to load converter: {e}") from e

    _report_electron_progress(20, 100, "Processing...", "single_progress")
    # Simulate incremental progress (real progress depends on the converter)
    for i in range(3, 9):
        time.sleep(0.05)
        _report_electron_progress(
            i * 10, 100, f"Converting ({i * 10}%)", "single_progress"
        )

    # Perform the actual conversion
    try:
        _report_electron_progress(90, 100, "Finalizing...", "single_progress")
        result_path = converter_callable(input_path, output_path, **kwargs)
        _report_electron_progress(100, 100, "Complete", "single_complete")
        logger.info(f"Single conversion successful: {result_path}")
        return result_path
    except Exception as e:
        logger.exception(f"Error during single conversion: {e}")
        _report_electron_progress(100, 100, f"Error: {e}", "single_error")
        raise


def main() -> int:
    """Main entry point for the Electron bridge script.

    This function is executed when the script is run. It parses command-line
    arguments, determines whether to perform a single or batch conversion,
    invokes the appropriate conversion logic, and reports results/errors to
    Electron via stdout using prefixed JSON messages (PROGRESS:, RESULT:, ERROR:, BATCH_PROGRESS:, BATCH_RESULT:).

    The script expects arguments defining the conversion type, input file(s),
    optional output directory, and other converter-specific options.

    Returns:
        int: Exit code of the process. 0 for success, 1 for general errors,
             2 for argument parsing errors.
    """
    logger = LogManager().get_bridge_logger()

    parser = argparse.ArgumentParser(description="MDtoPDF Electron Bridge")

    # Fix command line args - better organize subparsers
    parser.add_argument(
        "conversion_type", help="Type of conversion (e.g., pdf2md, md2pdf)"
    )
    parser.add_argument(
        "--input-files", nargs="+", required=True, help="One or more input file paths"
    )
    parser.add_argument(
        "--output-dir", help="Output directory for converted files (optional)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,  # Default will be taken from config
        help="Number of worker threads for batch processing",
    )
    # Add known converter options as arguments
    # PDF2MD specific
    parser.add_argument(
        "--engine", help="Specify conversion engine (pdf2md, html2pdf, etc.)"
    )
    parser.add_argument("--lang", help="OCR language(s)")
    parser.add_argument("--dpi", type=int, help="OCR DPI")
    parser.add_argument(
        "--force-ocr", action="store_true", help="Force OCR on all pages"
    )
    parser.add_argument("--psm", type=int, help="Tesseract PSM")
    parser.add_argument("--oem", type=int, help="Tesseract OEM")
    # PDF2EDITABLE specific new options
    parser.add_argument(
        "--redo-ocr",
        action="store_true",
        help="Redo OCR, stripping old OCR but preserving visible text.",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Use unpaper to clean image before OCR."
    )
    parser.add_argument(
        "--deskew", action="store_true", help="Deskew pages before OCR."
    )
    parser.add_argument(
        "--output-type",
        choices=["pdf", "pdfa"],
        help="Output type for PDF ('pdf' or 'pdfa'). Default: OCRmyPDF's default (usually 'pdfa' unless specified).",
    )
    parser.add_argument(
        "--pdf-renderer",
        choices=["auto", "hocr", "sandwich"],
        help="PDF renderer to use ('auto', 'hocr', 'sandwich'). Default: OCRmyPDF's default ('auto').",
    )
    # MD2PDF specific
    parser.add_argument("--page-break-marker", help="Custom page break marker")
    # DOCX2MD specific
    parser.add_argument("--style-map", help="Path to DOCX style map JSON")
    parser.add_argument("--image-dir", help="Directory for extracted DOCX images")
    # MD2DOCX specific
    parser.add_argument(
        "--reference-docx",
        help="Path to a reference DOCX file for styling output of md2docx conversion.",
    )
    # PDF2EDITABLE specific ( reusing --lang and --force-ocr from PDF2MD for consistency if applicable)
    # --lang is already defined for PDF2MD, can be reused.
    # --force-ocr is already defined for PDF2MD, can be reused.
    # If these need to be distinctly named or handled, new args would be added.
    # For now, assuming they can be shared if the meaning is consistent.

    try:
        args = parser.parse_args()
    except SystemExit as e:  # Catch argparse errors
        logger.error(f"Argument parsing error: {e}")
        # Send error message back to Electron if possible
        error_data = {"type": "error", "message": "Invalid command line arguments."}
        print(f"ERROR: {json.dumps(error_data)}")
        sys.stdout.flush()
        return 2  # Indicate argument error

    # --- Prepare options ---
    input_files_str = args.input_files
    output_dir = args.output_dir
    conversion_type = args.conversion_type
    max_workers = args.workers  # Will be None if not provided

    # Convert input file strings to Path objects
    input_files = [Path(f).resolve() for f in input_files_str]

    # --- Basic Input Validation ---
    invalid_files = []
    for file_path in input_files:
        if not file_path.exists():
            invalid_files.append(str(file_path))
        else:
            # Check extension compatibility early only if file exists
            try:
                check_file_extension_compatibility(conversion_type, file_path)
            except ValueError as e:
                # Report error and exit if any file is incompatible
                logger.error(f"Input validation error: {e}")
                error_data = {"type": "error", "message": str(e)}
                print(f"ERROR: {json.dumps(error_data)}")
                sys.stdout.flush()
                return 1

    if invalid_files:
        error_msg = f"Input file(s) not found: {', '.join(invalid_files)}"
        logger.error(error_msg)
        error_data = {"type": "error", "message": error_msg}
        print(f"ERROR: {json.dumps(error_data)}")
        sys.stdout.flush()
        return 1

    # Collect converter-specific options from args
    converter_options = {}
    if args.engine:
        converter_options["engine"] = args.engine
    if args.lang:
        converter_options["lang"] = args.lang
    if args.dpi:
        converter_options["dpi"] = args.dpi
    # Boolean flags: args.force_ocr will be True if --force-ocr is present, False otherwise.
    # We pass these directly to the converter function which expects booleans.
    converter_options["force_ocr"] = args.force_ocr
    converter_options["redo_ocr"] = args.redo_ocr
    converter_options["clean"] = args.clean
    converter_options["deskew"] = args.deskew

    if args.psm:
        converter_options["psm"] = args.psm
    if args.oem:
        converter_options["oem"] = args.oem
    if args.page_break_marker:
        converter_options["page_break_marker"] = args.page_break_marker
    if args.style_map:
        converter_options["style_map"] = args.style_map
    if args.image_dir:
        converter_options["image_dir"] = args.image_dir
    # Add reference_docx to converter_options
    if args.reference_docx:
        converter_options["reference_docx"] = args.reference_docx

    # String choice options: these will be None if not provided, or the chosen string.
    if args.output_type:
        converter_options["output_type"] = args.output_type
    if args.pdf_renderer:
        converter_options["pdf_renderer"] = args.pdf_renderer

    logger.info(
        f"Received request: Type={conversion_type}, Inputs={len(input_files)}, Output={output_dir}, Workers={max_workers or 'Default'}"
    )
    logger.debug(f"Converter options from args: {converter_options}")

    try:
        if len(input_files) == 1:
            # Single file conversion
            logger.info("Processing as single file conversion.")
            input_path = input_files[0]
            # For single file, output_dir acts as specified output directory
            # The convert_with_progress function now handles directory vs file path
            output_path_arg = Path(output_dir) if output_dir else None

            result_path = convert_with_progress(
                conversion_type,
                input_path,
                output_path_arg,
                **converter_options,
            )
            # Report final success for single file
            success_data = {
                "type": "single_result",
                "success": True,
                "outputPath": str(result_path),
            }
            print(f"RESULT: {json.dumps(success_data)}")
            sys.stdout.flush()
            return 0
        else:
            # Batch conversion
            logger.info("Processing as batch file conversion.")
            # Pass the callback to the batch processor
            summary = run_batch(
                conversion_type=conversion_type,
                input_files=input_files,  # type: ignore[arg-type] # Pass list of Path objects
                output_dir=output_dir,
                max_workers=max_workers,  # Pass None to use config default
                progress_callback=_report_electron_batch_progress,
                **converter_options,
            )
            # Report final batch summary
            print(f"BATCH_RESULT: {json.dumps(summary)}")
            sys.stdout.flush()
            # Return success if at least one file converted, otherwise error
            return 0 if summary["successful"] > 0 else 1

    except (ImportError, FileNotFoundError, ValueError) as e:
        logger.error(f"Configuration or Input Error: {e}")
        error_data = {"type": "error", "message": str(e)}
        print(f"ERROR: {json.dumps(error_data)}")
        sys.stdout.flush()
        return 1
    except Exception as e:
        logger.exception(f"Unhandled error during conversion: {e}")
        error_data = {"type": "error", "message": f"An unexpected error occurred: {e}"}
        print(f"ERROR: {json.dumps(error_data)}")
        sys.stdout.flush()
        return 1


if __name__ == "__main__":
    # Ensure LogManager can initialize if needed for the final message
    final_logger = None
    try:
        log_manager_init_check = LogManager()
        final_logger = log_manager_init_check.get_logger("main_entry")
    except Exception as init_err:
        # If logging setup fails critically, print error and exit
        print(
            f"ERROR: Failed to initialize logging system: {init_err}", file=sys.stderr
        )
        sys.exit(99)  # Use a distinct exit code for logging failure

    exit_code = main()  # Run the main logic

    # Log the final exit code if logger was obtained successfully
    if final_logger:
        final_logger.info(
            f"Electron bridge process finished with exit code: {exit_code}"
        )
    else:
        # Fallback print if logger failed but main ran
        print(f"INFO: Electron bridge process finished with exit code: {exit_code}")

    sys.exit(exit_code)
