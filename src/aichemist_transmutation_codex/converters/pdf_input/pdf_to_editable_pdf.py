"""PDF to Editable PDF Converter using OCRmyPDF.

This module provides functionality to convert non-editable (e.g., scanned) PDFs
into PDFs with a text layer, making them searchable and text-selectable.
It relies on OCRmyPDF, which in turn uses the Tesseract OCR engine.
"""

from pathlib import Path
from typing import Any

import ocrmypdf

# Import specific exceptions directly
from ocrmypdf.exceptions import InputFileError, MissingDependencyError

from aichemist_transmutation_codex.config import (
    LogManager,  # Assuming LogManager is accessible
)

# It's good practice to get a logger specific to this module.
# The name 'pdf_to_editable_pdf_converter' clearly identifies the source of logs.
logger = LogManager().get_logger("pdf_to_editable_pdf_converter")


def convert_pdf_to_editable(
    input_path: str | Path,
    output_path: str | Path | None = None,
    lang: str = "eng",
    force_ocr: bool = False,
    **kwargs: Any,
) -> Path:
    """Converts a PDF to an editable PDF by adding an OCR text layer.

    "Editable" here means the PDF will have selectable and searchable text.
    It does not mean the PDF structure becomes like a word processing document.

    Args:
        input_path: Path to the input PDF file.
        output_path: Path to save the output editable PDF file.
                     If None, it defaults to the input directory with "_editable" suffix.
        lang: Language(s) for OCR, e.g., "eng" for English, "eng+fra" for English and French.
              This corresponds to Tesseract language codes.
        force_ocr: If True, forces OCR on pages that already have text.
                   Otherwise, OCRmyPDF tries to respect existing text.
        **kwargs: Additional keyword arguments to pass to ocrmypdf.ocr().
                  Useful for advanced options like --deskew, --clean, etc.

    Returns:
        Path to the generated editable PDF file.

    Raises:
        FileNotFoundError: If the input_path does not exist.
        MissingDependencyError: If Tesseract or its language packs are not installed correctly.
        InputFileError: If OCRmyPDF encounters an issue with the input file.
        Exception: For other unexpected errors during conversion.
    """
    # Resolve the input path to an absolute path and check if it exists.
    # This helps in providing clearer error messages and ensures the path is valid.
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input PDF not found: {input_path}")
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    # Determine the output path if not provided.
    # The convention is to save the output in the same directory as the input,
    # with "_editable" appended to the original filename before the extension.
    if output_path is None:
        output_path = input_path.with_name(
            f"{input_path.stem}_editable{input_path.suffix}"
        )
    else:
        # If an output_path is provided, resolve it to an absolute path.
        # Also, ensure the parent directory for the output file exists.
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting PDF to Editable PDF conversion for: {input_path.name}")
    logger.info(f"Output will be saved to: {output_path}")
    logger.info(f"OCR Language: {lang}, Force OCR: {force_ocr}")
    if kwargs:
        logger.info(f"Additional OCRmyPDF options: {kwargs}")

    try:
        # This is the core call to OCRmyPDF.
        # `input_file` and `output_file` are the primary arguments.
        # `language` specifies the OCR language(s).
        # `force_ocr` controls whether to re-OCR pages with existing text.
        # `redo_ocr`, `output_type`, `clean`, `deskew`, `pdf_renderer` etc.,
        # will now come from kwargs if provided by the user via the GUI.
        # If not in kwargs, OCRmyPDF's defaults for those parameters will apply.
        ocrmypdf.ocr(
            input_file=input_path,
            output_file=output_path,
            language=lang,
            force_ocr=force_ocr,
            progress_bar=False,  # Assuming progress is handled by electron_bridge
            **kwargs,
        )
        logger.info(
            f"Successfully converted {input_path.name} to editable PDF: {output_path}"
        )
        return output_path
    except MissingDependencyError as e:
        # This is a common error if Tesseract or its language packs are not installed correctly.
        logger.error(
            f"Missing dependency for OCRmyPDF (likely Tesseract or language packs): {e}"
        )
        logger.error(
            "Please ensure Tesseract OCR is installed and in your system PATH, "
            "and that the required language packs (e.g., for '{lang}') are installed."
        )
        raise  # Re-raise the exception to be handled by the calling code (e.g., electron_bridge)
    except InputFileError as e:
        logger.error(
            f"OCRmyPDF encountered an issue with the input file {input_path.name}: {e}"
        )
        raise
    except Exception as e:
        # Catch any other unexpected exceptions during the OCR process.
        logger.exception(
            f"An unexpected error occurred during PDF to Editable PDF conversion for {input_path.name}: {e}"
        )
        raise


if __name__ == "__main__":
    # This section provides a simple way to test the converter directly from the command line.
    # It's useful for development and debugging.
    # Example usage:
    # python src/mdtopdf/converters/pdf_to_editable_pdf.py path/to/your/scanned.pdf path/to/your/output_editable.pdf --lang eng

    import argparse
    import logging  # Import logging for basicConfig

    # Configure basic logging for the command-line test.
    # This helps in seeing log messages when running the script directly.
    # This will set up a simple console logger.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # The main LogManager instance for the converter will still be created
    # when convert_pdf_to_editable is called, using its own configuration.
    # This basicConfig is primarily for the __main__ block's direct operations.

    parser = argparse.ArgumentParser(
        description="Convert a scanned PDF to an editable PDF using OCRmyPDF."
    )
    parser.add_argument("input_pdf", type=Path, help="Path to the input PDF file.")
    parser.add_argument(
        "output_pdf",
        type=Path,
        nargs="?",  # Makes output_pdf optional
        help="Path to the output editable PDF file (optional). Defaults to input_directory/input_name_editable.pdf",
    )
    parser.add_argument(
        "--lang",
        default="eng",
        help="OCR language(s) for Tesseract (e.g., 'eng', 'fra', 'eng+fra'). Default: 'eng'.",
    )
    parser.add_argument(
        "--force-ocr",
        action="store_true",
        help="Force OCR even if text is already present.",
    )
    # Add more arguments for other ocrmypdf options if needed for testing, e.g., --deskew

    args = parser.parse_args()

    try:
        logger.info("Running PDF to Editable PDF converter from command line...")
        # Call the conversion function with arguments from the command line.
        result_path = convert_pdf_to_editable(
            args.input_pdf, args.output_pdf, lang=args.lang, force_ocr=args.force_ocr
        )
        logger.info(f"Command line conversion successful. Output at: {result_path}")
    except FileNotFoundError:
        logger.error(f"Error: Input file not found at {args.input_pdf}")
    except MissingDependencyError:
        logger.error(
            "Error: Missing Tesseract or other OCRmyPDF dependency. "
            "Ensure Tesseract is installed and in PATH with required language data."
        )
    except Exception as e:
        logger.error(f"An error occurred during command line conversion: {e}")
