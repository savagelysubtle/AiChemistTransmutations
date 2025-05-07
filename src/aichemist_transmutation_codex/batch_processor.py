"""
Batch Processing Engine.

This module provides a centralized, reusable batch processing engine for converting
files between different formats, with support for concurrent processing and progress tracking.
"""

import concurrent.futures
import importlib
import threading
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from mdtopdf.config import ConfigManager, LogManager

# Setup logger
log_manager = LogManager()
logger = log_manager.get_batch_logger()

# Type aliases
ProgressCallback = Callable[[int, int, str, bool, float, str | None], None]
ConversionResult = tuple[Path, bool, float, str | None]
BatchSummary = dict[str, Any]


def _process_single_file_wrapper(
    converter_func: Callable,
    input_path: Path,
    output_dir: Path | None,
    converter_options: dict[str, Any],
    # Add a logger specific to this worker/file if needed, or use the main one
) -> ConversionResult:
    """
    Wrapper function to process a single file with error handling.
    """
    start_time = time.time()
    error_msg = None
    output_path = input_path.with_suffix(".failed")  # Default fail path

    logger.info(f"Starting processing for: {input_path.name}")
    try:
        # Determine output path if not specified
        if output_dir:
            # Construct output path in the specified directory
            # The converter function should handle the final extension
            output_path_option = output_dir / input_path.name
            converter_options["output_path"] = output_path_option
            logger.debug(f"Setting potential output path: {output_path_option}")
        else:
            # If no output_dir, converter usually defaults to same dir as input
            # Remove explicit output_path if it was set from a previous failed run
            converter_options.pop("output_path", None)

        # Call the converter function
        result_path = converter_func(input_path, **converter_options)
        success = True
        logger.info(f"Successfully processed: {input_path.name} -> {result_path.name}")
        return result_path, success, time.time() - start_time, None

    except Exception as e:
        logger.exception(f"Error processing {input_path.name}")
        error_msg = str(e)
        # Use the output path determined earlier if possible, otherwise default fail path
        failed_output_path = converter_options.get("output_path", output_path)
        return (
            failed_output_path.with_suffix(".failed"),
            False,
            time.time() - start_time,
            error_msg,
        )


def run_batch(
    conversion_type: str,
    input_files: list[str | Path],
    output_dir: str | Path | None = None,
    max_workers: int | None = None,
    progress_callback: ProgressCallback | None = None,
    **converter_options: Any,
) -> BatchSummary:
    """
    Run a batch conversion job with concurrent processing.
    """
    # Convert paths
    input_paths = [Path(f) for f in input_files]
    output_dir_path = Path(output_dir) if output_dir else None

    # Get configuration
    config = ConfigManager()
    # app_settings = config.get_config("application") # Removed unused variable
    # Use max_workers from args, then config, then default
    if max_workers is None:
        max_workers = config.get_value("application", "max_workers", 4)
    logger.info(
        f"Running batch conversion: {conversion_type} with {max_workers} workers"
    )

    # Ensure output dir exists
    if output_dir_path:
        output_dir_path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir_path}")

    # Map conversion type
    # Consider moving this map to config or a dedicated module
    conversion_map = {
        "pdf2md": ("converters.pdf_to_markdown", "PDFToMarkdownConverter", "convert"),
        "md2pdf": ("converters.markdown_to_pdf", None, "convert_md_to_pdf"),
        "html2pdf": ("converters.html_to_pdf", None, "convert_html_to_pdf"),
        "md2html": ("converters.markdown_to_html", None, "convert_md_to_html"),
        "pdf2html": ("converters.pdf_to_html", None, "convert_pdf_to_html"),
        "docx2md": ("converters.docx_to_markdown", None, "convert_docx_to_md"),
    }

    if conversion_type not in conversion_map:
        logger.error(f"Unsupported conversion type: {conversion_type}")
        raise ValueError(f"Unsupported conversion type: {conversion_type}")

    module_path, class_name, func_name = conversion_map[conversion_type]

    # Import and get the callable (function or class method)
    try:
        logger.debug(f"Importing module: . {module_path} from package mdtopdf")
        module = importlib.import_module(f".{module_path}", package="mdtopdf")
        if class_name:
            ConverterClass = getattr(module, class_name)
            # Instantiate the converter class (it might use config internally)
            converter_instance = ConverterClass()
            converter_callable = getattr(converter_instance, func_name)
        else:
            converter_callable = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        logger.exception(
            f"Failed to import or find converter for {conversion_type}: {e}"
        )
        raise ImportError(
            f"Failed to import converter for {conversion_type}: {e}"
        ) from e

    total_files = len(input_paths)
    successful = 0
    failed = 0
    results = []
    start_time = time.time()
    progress_lock = (
        threading.Lock()
    )  # Lock for updating shared counters if callback does
    processed_count = 0

    logger.info(f"Starting batch processing of {total_files} files.")

    # Use ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                _process_single_file_wrapper,
                converter_callable,  # Pass the specific function/method
                input_path,
                output_dir_path,
                converter_options.copy(),  # Pass copy to avoid race conditions if modified
            ): input_path
            for input_path in input_paths
        }

        for future in concurrent.futures.as_completed(future_to_file):
            input_path = future_to_file[future]
            with progress_lock:
                processed_count += 1
                current_index = processed_count

            try:
                output_path, success, proc_time, error = future.result()
                if success:
                    successful += 1
                else:
                    failed += 1

                result = {
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "success": success,
                    "time": proc_time,
                    "error": error,
                }
                results.append(result)
                logger.debug(
                    f"Completed {input_path.name} (Success: {success}, Time: {proc_time:.2f}s)"
                )

                if progress_callback:
                    try:
                        progress_callback(
                            current_index,
                            total_files,
                            str(input_path),
                            success,
                            proc_time,
                            error,
                        )
                    except Exception as cb_err:
                        logger.error(
                            f"Progress callback failed for {input_path.name}: {cb_err}"
                        )

            except Exception as e:
                logger.exception(
                    f"Error processing future result for {input_path.name}"
                )
                failed += 1
                results.append(
                    {
                        "input_path": str(input_path),
                        "output_path": str(input_path.with_suffix(".failed")),
                        "success": False,
                        "time": time.time() - start_time,  # Use total time as estimate
                        "error": str(e),
                    }
                )
                # Optionally call progress callback for the failure
                if progress_callback:
                    try:
                        progress_callback(
                            current_index,
                            total_files,
                            str(input_path),
                            False,
                            0.0,
                            str(e),
                        )
                    except Exception as cb_err:
                        logger.error(
                            f"Progress callback failed for {input_path.name} after future exception: {cb_err}"
                        )

    # Prepare summary
    total_time = time.time() - start_time
    logger.info(
        f"Batch processing finished in {total_time:.2f}s. Successful: {successful}, Failed: {failed}"
    )
    summary = {
        "total_files": total_files,
        "successful": successful,
        "failed": failed,
        "total_time": total_time,
        "results": sorted(
            results, key=lambda x: x["input_path"]
        ),  # Sort results by input path
    }

    return summary
