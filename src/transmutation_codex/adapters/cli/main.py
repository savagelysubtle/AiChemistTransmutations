#!/usr/bin/env python
"""MDtoPDF CLI module.

Provides a command-line interface for the MDtoPDF converter.
"""

import argparse
import importlib
import sys
from pathlib import Path

from transmutation_codex.core.logger import LogManager
from transmutation_codex.core.settings import ConfigManager

# Initialize LogManager (loads config and sets up logging)
log_manager = LogManager()
logger = log_manager.get_logger("cli")


def main() -> int:
    """Runs the MDtoPDF command-line interface application.

    Parses command-line arguments, sets up converter options, dynamically imports
    and calls the appropriate converter function, and handles GUI launch requests.

    Returns:
        int: 0 on successful conversion or GUI launch, 1 on error.
    """
    parser = argparse.ArgumentParser(description="MDtoPDF Converter CLI")

    # Get config for defaults
    config = ConfigManager()
    pdf2md_defaults = config.get_converter_config("pdf2md")

    parser.add_argument(
        "conversion_type",
        choices=["md2pdf", "md2html", "pdf2md", "pdf2html", "html2pdf", "docx2md", "txt2pdf"],
        help="Type of conversion (e.g., pdf2md, md2html, txt2pdf)",
    )
    parser.add_argument("input_path", help="Input file path")
    parser.add_argument("--output", help="Output file path (optional)")

    # GUI argument (less relevant now, but kept for structure)
    parser.add_argument(
        "--gui", action="store_true", help="Launch the GUI interface (if available)"
    )

    # PDF to Markdown specific options
    pdf2md_group = parser.add_argument_group("PDF to Markdown Options")
    pdf2md_group.add_argument(
        "--engine",
        choices=["basic", "ocr", "enhanced_ocr", "pymupdf4llm"],
        default=pdf2md_defaults.get("engine", "enhanced_ocr"),
        help="PDF to Markdown engine to use (default: %(default)s)",
    )
    pdf2md_group.add_argument(
        "--lang",
        default=pdf2md_defaults.get("ocr_languages", "eng"),
        help="Language(s) for OCR (default: %(default)s). Use + to combine (e.g., eng+fra)",
    )
    pdf2md_group.add_argument(
        "--dpi",
        type=int,
        default=pdf2md_defaults.get("ocr_dpi", 300),
        help="Resolution for OCR scanning in DPI (default: %(default)s)",
    )
    pdf2md_group.add_argument(
        "--force-ocr",
        action="store_true",
        default=pdf2md_defaults.get("force_ocr", False),
        help="Force OCR on all pages, even if text is present",
    )
    pdf2md_group.add_argument(
        "--psm",
        type=int,
        default=pdf2md_defaults.get("ocr_psm", 1),
        help="Page segmentation mode for Tesseract (1-13, default: %(default)s)",
    )
    pdf2md_group.add_argument(
        "--oem",
        type=int,
        default=pdf2md_defaults.get("ocr_oem", 3),
        help="OCR Engine mode for Tesseract (0-3, default: %(default)s)",
    )

    # Markdown to PDF specific options
    md2pdf_group = parser.add_argument_group("Markdown to PDF Options")
    md2pdf_group.add_argument(
        "--page-break-marker",
        default=config.get_value("md2pdf", "page_break_marker", "<!-- pagebreak -->"),
        help="Custom page break marker (default: %(default)s)",
    )

    # DOCX to Markdown specific options
    docx2md_group = parser.add_argument_group("DOCX to Markdown Options")
    docx2md_group.add_argument("--style-map", help="Path to custom style map JSON")
    docx2md_group.add_argument(
        "--image-dir",
        default=config.get_value("docx2md", "image_dir", "images"),
        help="Directory for extracted images (default: %(default)s)",
    )
    docx2md_group.add_argument(
        "--use-mammoth",
        action="store_true",
        default=config.get_value("docx2md", "use_mammoth", False),
        help="Prefer Mammoth engine",
    )

    # TXT to PDF specific options
    txt2pdf_group = parser.add_argument_group("TXT to PDF Options")
    txt2pdf_group.add_argument(
        "--font-name",
        default=config.get_value("txt2pdf", "font_name", "Helvetica"),
        help="Font name for PDF output (default: %(default)s)",
    )
    txt2pdf_group.add_argument(
        "--font-size",
        type=int,
        default=config.get_value("txt2pdf", "font_size", 10),
        help="Font size for PDF output (default: %(default)s)",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        logger.error(f"Argument parsing failed: {e}")
        return 1  # Exit code for argument errors

    # --- GUI Launch Logic (Optional) --- #
    if args.gui:
        logger.info("GUI launch requested via CLI...")
        try:
            from mdtopdf.gui.customtkgui import run_ctk_gui  # type: ignore

            logger.info("Attempting to start CustomTkinter GUI...")
            return run_ctk_gui()
        except ImportError:
            logger.warning("CustomTkinter GUI not available.")
            try:
                from mdtopdf.gui import run_gui  # type: ignore

                logger.info("Attempting to start PySimpleGUI...")
                return run_gui()
            except ImportError as gui_err:
                logger.error(f"No GUI libraries found: {gui_err}")
                print(
                    "Error: GUI requested but no GUI library (CustomTkinter or PySimpleGUI) is installed.",
                    file=sys.stderr,
                )
                return 1

    # --- CLI Conversion Logic --- #
    logger.info(f"Starting {args.conversion_type} conversion: {args.input_path}")

    # Prepare converter options from args
    converter_options = {}
    if args.conversion_type == "pdf2md":
        converter_options["engine"] = args.engine
        converter_options["lang"] = args.lang
        converter_options["dpi"] = args.dpi
        converter_options["force_ocr"] = args.force_ocr
        converter_options["psm"] = args.psm
        converter_options["oem"] = args.oem
    elif args.conversion_type == "md2pdf":
        converter_options["page_break_marker"] = args.page_break_marker
    elif args.conversion_type == "docx2md":
        converter_options["style_map"] = args.style_map
        converter_options["image_dir"] = args.image_dir
        converter_options["use_mammoth"] = args.use_mammoth
    elif args.conversion_type == "txt2pdf":
        converter_options["font_name"] = args.font_name
        converter_options["font_size"] = args.font_size
    # Add options for other converters if needed

    logger.debug(f"Converter options: {converter_options}")

    try:
        # Import the appropriate converter function or class method dynamically
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
            "txt2pdf": ("plugins.txt.to_pdf", None, "convert_txt_to_pdf"),
        }

        if args.conversion_type not in conversion_map:
            logger.error(f"Invalid conversion type provided: {args.conversion_type}")
            raise ValueError(f"Invalid conversion type: {args.conversion_type}")

        module_path, class_name, func_name = conversion_map[args.conversion_type]

        # Dynamically import the module within mdtopdf package
        try:
            module = importlib.import_module(
                f".{module_path}", package="transmutation_codex"
            )
        except ImportError as import_err:
            logger.error(
                f"Failed to import converter module '{module_path}': {import_err}"
            )
            logger.error(
                f"Make sure the necessary dependencies for '{args.conversion_type}' are installed."
            )
            raise ImportError(f"Could not import {module_path}") from import_err

        # Get the callable (function or class method)
        if class_name:
            ConverterClass = getattr(module, class_name)
            converter_instance = (
                ConverterClass()
            )  # Instantiates using its own __init__ (which uses config)
            converter_callable = getattr(converter_instance, func_name)
        else:
            converter_callable = getattr(module, func_name)

        input_path = Path(args.input_path)
        output_path: Path | None = Path(args.output) if args.output else None

        # Perform the conversion
        result_path = converter_callable(input_path, output_path, **converter_options)

        logger.info(f"Conversion successful. Output saved to: {result_path}")
        print(f"Output saved to: {result_path}")  # User feedback
        return 0  # Success

    except (FileNotFoundError, ValueError, ImportError) as e:
        logger.error(f"Conversion failed: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1  # Failure
    except Exception as e:
        logger.exception(f"An unexpected error occurred during conversion: {e}")
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1  # Failure


if __name__ == "__main__":
    # Logging is configured when LogManager is first initialized.
    # No need to call basicConfig here.
    exit_code = main()
    logger.info(f"CLI process finished with exit code: {exit_code}")
    sys.exit(exit_code)
