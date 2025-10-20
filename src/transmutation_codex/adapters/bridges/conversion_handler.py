"""Conversion handling for bridge operations.

This module contains the core logic for executing conversions through the bridge,
with integrated progress reporting and error handling.
"""

import time
from pathlib import Path
from typing import Any

from transmutation_codex.core import get_log_manager, get_registry
from transmutation_codex.services.batcher import run_batch

from .argument_parser import BridgeArguments
from .base import BridgeConversionError, format_duration, send_batch_result
from .progress_reporter import BatchProgressReporter, ProgressReporter


def handle_single_conversion(
    args: BridgeArguments, reporter: ProgressReporter
) -> dict[str, Any]:
    """Handle a single file conversion.

    Args:
        args: Parsed bridge arguments
        reporter: Progress reporter

    Returns:
        Dictionary with conversion results

    Raises:
        BridgeConversionError: If conversion fails
    """
    logger = get_log_manager().get_bridge_logger()

    # Start operation
    reporter.start_operation(100, "Initializing conversion...")

    # Import plugins to trigger auto-registration
    reporter.report(10, 100, "Loading converter...")
    try:
        import transmutation_codex.plugins  # noqa: F401
    except ImportError as e:
        logger.error(f"Failed to import plugins: {e}")
        raise BridgeConversionError(f"Failed to load plugins: {e}") from e

    # Get the plugin registry
    registry = get_registry()

    # Parse conversion type (e.g., "pdf2md" -> "pdf", "md")
    if "2" not in args.conversion_type:
        raise BridgeConversionError(
            f"Invalid conversion type format: {args.conversion_type}. "
            "Expected format: source2target"
        )

    source_format, target_format = args.conversion_type.split("2", 1)

    # Get converter from registry
    reporter.report(20, 100, f"Finding converter for {args.conversion_type}...")

    plugin_info = registry.get_converter(source_format, target_format)

    if not plugin_info:
        # Get available conversions for better error message
        available = registry.get_available_conversions()
        available_str = ", ".join(
            f"{src}2{tgt}" for src, targets in available.items() for tgt in targets
        )
        raise BridgeConversionError(
            f"No converter found for '{args.conversion_type}'. "
            f"Available: {available_str or 'none'}"
        )

    logger.info(
        f"Using converter: {plugin_info.name} "
        f"(priority: {plugin_info.priority}, version: {plugin_info.version})"
    )

    # Set current file
    input_path = Path(args.input_path)
    reporter.set_current_file(input_path.name)

    # Prepare output path
    if args.output_path:
        output_path = Path(args.output_path)
    else:
        # Auto-generate output path
        output_path = input_path.with_suffix(f".{target_format}")

    reporter.report(30, 100, f"Converting {input_path.name}...")

    # Execute conversion
    start_time = time.time()
    try:
        converter_callable = plugin_info.converter_function

        # Call converter with options
        try:
            result_path = converter_callable(
                str(input_path), str(output_path), **args.options
            )
        except Exception as first_error:
            # Special handling for PDF to Editable: retry with force-ocr if it fails
            if target_format == "editable" and source_format == "pdf":
                # Check if the error is about existing text (PriorOcrFoundError)
                error_msg = str(first_error).lower()
                if "already has text" in error_msg or "priorocrfound" in error_msg:
                    logger.info(
                        f"PDF already has text, retrying with force-ocr enabled for {input_path.name}"
                    )
                    reporter.report(50, 100, "PDF has text, retrying with force OCR...")

                    # Retry with force_ocr enabled
                    retry_options = args.options.copy()
                    retry_options["force_ocr"] = True

                    result_path = converter_callable(
                        str(input_path), str(output_path), **retry_options
                    )
                    logger.info(f"Retry with force-ocr succeeded for {input_path.name}")
                else:
                    # Re-raise if it's a different error
                    raise
            else:
                # Re-raise for non-editable conversions
                raise

        duration = time.time() - start_time

        # Report success
        reporter.report(100, 100, f"Conversion complete in {format_duration(duration)}")
        reporter.report_success(
            f"Successfully converted {input_path.name} to {Path(result_path).name}",
            {
                "input_path": str(input_path),
                "output_path": str(result_path),
                "duration": duration,
                "converter": plugin_info.name,
            },
        )

        logger.info(
            f"Conversion successful: {input_path.name} -> {Path(result_path).name} "
            f"in {format_duration(duration)}"
        )

        return {
            "success": True,
            "input_path": str(input_path),
            "output_path": str(result_path),
            "duration": duration,
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.exception(f"Conversion failed: {e}")

        reporter.report_error(str(e), "conversion")
        reporter.report_failure(
            f"Conversion failed: {e}",
            {"input_path": str(input_path), "error": str(e), "duration": duration},
        )

        raise BridgeConversionError(f"Conversion failed: {e}") from e


def handle_batch_conversion(
    args: BridgeArguments, reporter: BatchProgressReporter
) -> dict[str, Any]:
    """Handle batch file conversion.

    Args:
        args: Parsed bridge arguments
        reporter: Batch progress reporter

    Returns:
        Dictionary with batch results

    Raises:
        BridgeConversionError: If batch conversion fails
    """
    logger = get_log_manager().get_bridge_logger()

    # Start batch
    total_files = len(args.input_files)
    reporter.start_batch(total_files)

    logger.info(
        f"Starting batch conversion: {total_files} files, type: {args.conversion_type}"
    )

    # Create progress callback
    def batch_progress_callback(
        current: int,
        total: int,
        input_file: str,
        success: bool,
        duration: float,
        error: str | None,
    ):
        """Callback for batch progress updates.

        Args:
            current: Current file index
            total: Total number of files
            input_file: Input file path
            success: Whether conversion succeeded
            duration: Conversion duration
            error: Error message if failed
        """
        filename = Path(input_file).name
        reporter.start_file(filename, current)
        reporter.complete_file(filename, success)

        if not success and error:
            logger.warning(f"File {current}/{total} failed: {filename} - {error}")

    # Run batch conversion
    start_time = time.time()
    try:
        summary = run_batch(
            conversion_type=args.conversion_type,
            input_files=args.input_files,
            output_dir=args.output_dir,
            progress_callback=batch_progress_callback,
            **args.options,
        )

        duration = time.time() - start_time

        # Complete batch
        reporter.complete_batch()

        # Send batch results
        send_batch_result(summary)

        logger.info(
            f"Batch conversion complete: {summary['successful']}/{summary['total_files']} successful "
            f"in {format_duration(duration)}"
        )

        return summary

    except Exception as e:
        duration = time.time() - start_time
        logger.exception(f"Batch conversion failed: {e}")

        reporter.report_error(str(e), "batch_conversion")
        reporter.report_failure(
            f"Batch conversion failed: {e}",
            {"total_files": total_files, "error": str(e), "duration": duration},
        )

        raise BridgeConversionError(f"Batch conversion failed: {e}") from e


def handle_pdf_merge(
    args: BridgeArguments, reporter: ProgressReporter
) -> dict[str, Any]:
    """Handle PDF merging operation.

    Args:
        args: Parsed bridge arguments
        reporter: Progress reporter

    Returns:
        Dictionary with merge results

    Raises:
        BridgeConversionError: If merge fails
    """
    logger = get_log_manager().get_bridge_logger()

    # Start operation
    total_files = len(args.input_files)
    reporter.start_operation(100, f"Merging {total_files} PDF files...")

    logger.info(f"Starting PDF merge: {total_files} files -> {args.output_path}")

    # Import merger
    reporter.report(20, 100, "Loading PDF merger...")
    try:
        from transmutation_codex.services.merger import (
            merge_multiple_pdfs_to_single_pdf,
        )
    except ImportError as e:
        logger.error(f"Failed to import PDF merger: {e}")
        raise BridgeConversionError(f"PDF merger not available: {e}") from e

    # Execute merge
    reporter.report(40, 100, "Merging PDF files...")
    start_time = time.time()

    try:
        result_path = merge_multiple_pdfs_to_single_pdf(
            args.input_files, args.output_path
        )

        duration = time.time() - start_time

        # Report success
        reporter.report(100, 100, f"Merge complete in {format_duration(duration)}")
        reporter.report_success(
            f"Successfully merged {total_files} PDFs",
            {
                "input_files": args.input_files,
                "output_path": str(result_path),
                "total_files": total_files,
                "duration": duration,
            },
        )

        logger.info(
            f"PDF merge successful: {total_files} files in {format_duration(duration)}"
        )

        return {
            "success": True,
            "output_path": str(result_path),
            "total_files": total_files,
            "duration": duration,
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.exception(f"PDF merge failed: {e}")

        reporter.report_error(str(e), "merge")
        reporter.report_failure(
            f"PDF merge failed: {e}",
            {"input_files": args.input_files, "error": str(e), "duration": duration},
        )

        raise BridgeConversionError(f"PDF merge failed: {e}") from e


def handle_conversion(args: BridgeArguments) -> int:
    """Main conversion handler that routes to appropriate operation.

    Args:
        args: Parsed bridge arguments

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    logger = get_log_manager().get_bridge_logger()

    try:
        if args.mode == "convert":
            reporter = ProgressReporter("single")
            handle_single_conversion(args, reporter)
            return 0

        elif args.mode == "batch":
            reporter = BatchProgressReporter()
            handle_batch_conversion(args, reporter)
            return 0

        elif args.mode == "merge":
            reporter = ProgressReporter("merge")
            handle_pdf_merge(args, reporter)
            return 0

        else:
            logger.error(f"Unknown mode: {args.mode}")
            return 1

    except BridgeConversionError as e:
        logger.error(f"Conversion error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1
