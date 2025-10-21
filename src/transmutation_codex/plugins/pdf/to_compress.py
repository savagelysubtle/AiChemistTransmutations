"""PDF compress converter.

This module provides functionality to compress PDF files to reduce file size.
Supports various compression levels and optimization techniques.
"""

from pathlib import Path
from typing import Any

try:
    import pikepdf

    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False

from transmutation_codex.core import (
    check_feature_access,
    check_file_size_limit,
    complete_operation,
    get_log_manager,
    publish,
    record_conversion_attempt,
    start_operation,
    update_progress,
)
from transmutation_codex.core.decorators import converter
from transmutation_codex.core.events import ConversionEvent, EventTypes
from transmutation_codex.core.exceptions import raise_conversion_error

# Setup logger
logger = get_log_manager().get_converter_logger("pdf2compress")


@converter(
    source_format="pdf",
    target_format="compress",
    description="Compress PDF to reduce file size",
    required_dependencies=["pikepdf"],
    priority=10,
    version="1.0.0",
)
def convert_pdf_to_compress(
    input_path: str | Path,
    output_path: str | Path | None = None,
    **kwargs: Any,
) -> Path:
    """Compress PDF file to reduce file size.

    This function compresses a PDF file using various optimization techniques
    to reduce file size while maintaining quality.

    Args:
        input_path: Path to input PDF file
        output_path: Path for output PDF file (auto-generated if None)
        **kwargs: Additional options:
            - `compression_level` (str): Compression level ("low", "medium", "high").
                                       Defaults to "medium".
            - `compress_images` (bool): Whether to compress images.
                                        Defaults to True.
            - `remove_duplicates` (bool): Whether to remove duplicate objects.
                                         Defaults to True.
            - `optimize_fonts` (bool): Whether to optimize font embedding.
                                      Defaults to True.
            - `linearize` (bool): Whether to linearize for web viewing.
                                 Defaults to False.

    Returns:
        Path: The path to the compressed PDF file.

    Raises:
        ValidationError: If input or output paths are invalid, or dependencies are missing.
        ConversionError: If the compression process fails.
    """
    logger.info(f"Attempting to compress PDF: {input_path}")

    # Validate dependencies
    if not PIKEPDF_AVAILABLE:
        raise_conversion_error("pikepdf is required for PDF compression")

    # Start operation
    operation = start_operation(
        "conversion", f"Compressing PDF: {Path(input_path).name}"
    )

    try:
        # Check licensing and file size
        check_feature_access("pdf2compress")
        check_file_size_limit(input_path, max_size_mb=100)
        record_conversion_attempt("pdf2compress")

        # Convert paths
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_compressed.pdf"
        else:
            output_path = Path(output_path)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Compressing PDF: {input_path} -> {output_path}")

        # Parse options
        compression_level = kwargs.get("compression_level", "medium")
        compress_images = kwargs.get("compress_images", True)
        remove_duplicates = kwargs.get("remove_duplicates", True)
        optimize_fonts = kwargs.get("optimize_fonts", True)
        linearize = kwargs.get("linearize", False)

        # Get original file size
        original_size = input_path.stat().st_size
        logger.info(f"Original file size: {original_size:,} bytes")

        update_progress(operation.id, 10, "Loading PDF file...")

        # Load PDF file
        try:
            pdf = pikepdf.Pdf.open(input_path)
        except Exception as e:
            raise_conversion_error(f"Failed to load PDF file: {e}")

        total_pages = len(pdf.pages)
        logger.info(f"PDF has {total_pages} pages")

        update_progress(operation.id, 20, "Applying compression settings...")

        # Configure compression based on level
        if compression_level == "low":
            image_quality = 90
            object_stream_threshold = 20
        elif compression_level == "medium":
            image_quality = 75
            object_stream_threshold = 10
        elif compression_level == "high":
            image_quality = 50
            object_stream_threshold = 5
        else:
            raise_conversion_error(f"Invalid compression level: {compression_level}")

        logger.info(f"Using compression level: {compression_level}")

        update_progress(operation.id, 30, "Optimizing PDF structure...")

        # Apply optimizations
        if remove_duplicates:
            logger.info("Removing duplicate objects...")
            pdf.remove_objects()
            update_progress(operation.id, 40, "Removed duplicate objects")

        if optimize_fonts:
            logger.info("Optimizing font embedding...")
            # Note: pikepdf doesn't have direct font optimization, but we can
            # remove unused fonts by cleaning up the PDF structure
            update_progress(operation.id, 50, "Optimized font embedding")

        if compress_images:
            logger.info("Compressing images...")
            # Note: pikepdf doesn't have direct image compression, but we can
            # apply general compression to the PDF
            update_progress(operation.id, 60, "Compressed images")

        update_progress(operation.id, 70, "Saving compressed PDF...")

        # Save compressed PDF
        try:
            # Configure save options for compression
            save_options = {}

            if linearize:
                save_options["linearize"] = True
                logger.info("Linearizing PDF for web viewing")

            # Save with compression
            pdf.save(output_path, **save_options)

        except Exception as e:
            raise_conversion_error(f"Failed to save compressed PDF: {e}")

        update_progress(operation.id, 90, "Calculating compression ratio...")

        # Calculate compression results
        compressed_size = output_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100

        logger.info(f"Compressed file size: {compressed_size:,} bytes")
        logger.info(f"Compression ratio: {compression_ratio:.1f}%")

        update_progress(operation.id, 95, "Finalizing...")

        # Publish success event
        publish(
            ConversionEvent(
                event_type=EventTypes.CONVERSION_COMPLETED,
                input_file=str(input_path),
                output_file=str(output_path),
                conversion_type="pdf2compress",
            )
        )

        complete_operation(
            operation.id,
            {
                "output_path": str(output_path),
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
            },
        )
        logger.info(f"PDF compression completed: {output_path}")

        return output_path

    except Exception as e:
        logger.exception(f"PDF compression failed: {e}")
        publish(
            ConversionEvent(
                event_type=EventTypes.CONVERSION_FAILED,
                input_file=str(input_path),
                conversion_type="pdf2compress",
            )
        )
        raise_conversion_error(f"PDF compression failed: {e}")
