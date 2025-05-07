"""
PDF to Markdown converter.

This module provides functionality to convert PDF documents to Markdown format,
preserving document structure and formatting where possible.
"""

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from mdtopdf.config import ConfigManager, LogManager

# Setup logger using the LogManager singleton
log_manager = LogManager()
logger = log_manager.get_converter_logger("pdf2md")

try:
    import fitz  # PyMuPDF
except ImportError:
    logger.error("PyMuPDF is required but not installed. pip install pymupdf")
    fitz = None

# Try importing PyMuPDF4LLM
try:
    from pymupdf4llm import parse_pdf_to_markdown  # type: ignore

    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False
    logger.debug("PyMuPDF4LLM not available.")

    def parse_pdf_to_markdown(pdf_path: str) -> str:
        """Placeholder function when pymupdf4llm is not available."""
        logger.error(
            "PyMuPDF4LLM is required for this conversion engine. Install it with: pip install pymupdf4llm"
        )
        raise ImportError("PyMuPDF4LLM is not available.")


# Try importing OCR dependencies
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter

    # Get Tesseract path from config or use default
    config = ConfigManager()
    tesseract_cmd = config.get_value(
        "ocr", "tesseract_cmd", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # Set Tesseract path for Windows
    if Path(tesseract_cmd).exists():
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        TESSERACT_AVAILABLE = True
    else:
        logger.warning(f"Tesseract executable not found at: {tesseract_cmd}")
        TESSERACT_AVAILABLE = False
except ImportError:
    logger.warning("Pytesseract or PIL not installed. OCR functionality disabled.")
    TESSERACT_AVAILABLE = False

# For type checking only
if TYPE_CHECKING:
    import cv2
    import numpy as np

# Try importing OpenCV
try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore

    OPENCV_AVAILABLE = True
except ImportError:
    logger.debug("OpenCV not available. Advanced image processing will be limited.")
    OPENCV_AVAILABLE = False


class PDFToMarkdownConverter:
    def __init__(self):
        # Get configuration for pdf2md
        config = ConfigManager()
        self.settings = config.get_converter_config("pdf2md")
        self.logger = log_manager.get_converter_logger("pdf2md")

    def convert(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        **options: Any,
    ) -> Path:
        """Main conversion function, delegates based on config."""
        engine = options.get("engine", self.settings.get("engine", "enhanced_ocr"))
        self.logger.info(f"Using engine: {engine}")

        # Update settings with provided options
        merged_options = {**self.settings, **options}

        if engine == "pymupdf4llm":
            return convert_pdf_to_md_with_pymupdf4llm(
                input_path, output_path, **merged_options
            )
        elif engine == "enhanced_ocr":
            return convert_pdf_to_md_with_enhanced_ocr(
                input_path, output_path, **merged_options
            )
        elif engine == "ocr":
            return convert_pdf_to_md_with_ocr(input_path, output_path, **merged_options)
        elif engine == "basic":
            return convert_pdf_to_md(input_path, output_path, **merged_options)
        else:
            self.logger.error(
                f"Unknown pdf2md engine: {engine}. Defaulting to enhanced_ocr."
            )
            return convert_pdf_to_md_with_enhanced_ocr(
                input_path, output_path, **merged_options
            )


def _enhance_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Apply image enhancements to improve OCR accuracy.
    """
    logger.debug("Enhancing image for OCR...")
    # Step 1: Convert to grayscale
    if image.mode != "L":
        image = image.convert("L")
        logger.debug("Converted image to grayscale.")

    # Step 2: Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    logger.debug("Increased image contrast.")

    # Step 3: Apply sharpening
    image = image.filter(ImageFilter.SHARPEN)
    logger.debug("Applied sharpening filter.")

    if OPENCV_AVAILABLE:
        try:
            # Step 4: Apply bilateral filter for noise reduction
            img_array = np.array(image)
            img_array = cv2.bilateralFilter(img_array, 9, 75, 75)
            image = Image.fromarray(img_array)
            logger.debug("Applied bilateral filter.")

            # Step 5: Apply adaptive thresholding
            img_array = np.array(image)
            img_array = cv2.adaptiveThreshold(
                img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            image = Image.fromarray(img_array)
            logger.debug("Applied adaptive thresholding.")
        except Exception as e:
            logger.warning(f"OpenCV processing step failed: {e}")
    else:
        logger.debug("OpenCV not available, skipping advanced filtering.")

    return image


def _deskew_image(image: Image.Image) -> Image.Image:
    """
    Correct skewed text in images using OpenCV.
    """
    if not OPENCV_AVAILABLE:
        logger.debug("OpenCV not available, skipping deskew.")
        return image

    logger.debug("Deskewing image...")
    try:
        img_array = np.array(image)
        gray = (
            cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            if len(img_array.shape) == 3
            else img_array
        )
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) == 0:
            logger.debug("No text found for deskewing.")
            return image

        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle

        (h, w) = img_array.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            img_array, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        logger.debug(f"Deskewed image by {angle:.2f} degrees.")
        return Image.fromarray(rotated)
    except Exception as e:
        logger.warning(f"Deskewing failed: {e}")
        return image  # Return original if deskewing fails


def _extract_text_from_page(page: Any) -> str:
    """Attempt multiple extraction methods on a page and return the text."""
    methods = ["text", "html", "json", "dict"]
    for method in methods:
        try:
            text = page.get_text(method)
            if isinstance(text, str) and text.strip():
                if method == "html":
                    # Basic HTML cleaning
                    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL)
                    text = re.sub(r"<[^>]+>", " ", text)
                    text = re.sub(r"\s+", " ", text).strip()
                elif method == "json":
                    data = json.loads(text)
                    text = " ".join(
                        block.get("text", "") for block in data.get("blocks", [])
                    )
                elif method == "dict":
                    dict_data = page.get_text("dict")  # Already a dict
                    text_blocks = []
                    for block in dict_data.get("blocks", []):
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text_blocks.append(span.get("text", ""))
                    text = " ".join(text_blocks)

                if text.strip():
                    logger.debug(f"Extracted text using method: {method}")
                    return text
        except Exception as e:
            logger.debug(f"Text extraction method '{method}' failed: {e}")
    logger.warning("All text extraction methods failed for a page.")
    return ""


def _process_paragraphs(text: str) -> list[str]:
    """
    Process raw extracted text into cleaned paragraphs.
    """
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)  # Fix hyphenated words
    text = re.sub(r"\s*\n\s*", "\n\n", text)  # Normalize line breaks to double newlines
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return paragraphs


def convert_pdf_to_md(
    input_path: str | Path,
    output_path: str | Path | None = None,
    auto_ocr: bool = True,  # Kept for backward compatibility, use engine config
    **kwargs: Any,  # Catch other potential args
) -> Path:
    """
    Convert a PDF file to Markdown (Basic - text extraction only).
    """
    if fitz is None:
        logger.error("PyMuPDF is required for PDF conversion.")
        raise ImportError("PyMuPDF is required. Install it with: pip install pymupdf")

    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        logger.error(f"Invalid input file type: {input_path.suffix}")
        raise ValueError(f"Input file must be a PDF: {input_path}")

    output_path = (
        Path(output_path).resolve() if output_path else input_path.with_suffix(".md")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting {input_path} to Markdown (Basic)")
    try:
        pdf_document = fitz.open(str(input_path))
        md_lines = [f"# {input_path.stem}\n\n"]
        empty_pages = 0
        ocr_used = False  # Track if OCR was used for summary

        config = ConfigManager()
        settings = config.get_converter_config("pdf2md")
        # Use auto_ocr from args if passed, otherwise from config
        _auto_ocr = kwargs.get("auto_ocr", settings.get("ocr_enabled", True))
        ocr_available = _auto_ocr and TESSERACT_AVAILABLE
        ocr_lang = kwargs.get("lang", settings.get("ocr_languages", "eng"))
        ocr_dpi = kwargs.get("dpi", settings.get("ocr_dpi", 300))
        ocr_psm = kwargs.get("psm", settings.get("ocr_psm", 1))
        ocr_oem = kwargs.get("oem", settings.get("ocr_oem", 3))

        if _auto_ocr and not TESSERACT_AVAILABLE:
            logger.warning(
                "OCR requested but Tesseract is not available or configured."
            )

        if pdf_document.is_encrypted:
            logger.warning("PDF is encrypted. Authentication may be required.")
            try:
                pdf_document.authenticate("")
            except Exception as auth_e:
                logger.error(f"Failed to authenticate encrypted PDF: {auth_e}")
                md_lines.append("*Error: Failed to authenticate encrypted PDF.*\n\n")

        for page_num in range(pdf_document.page_count):
            logger.debug(f"Processing page {page_num + 1}")
            page = pdf_document.load_page(page_num)
            text = _extract_text_from_page(page)
            md_lines.append(f"## Page {page_num + 1}\n\n")

            if not text.strip() and ocr_available:
                logger.info(f"No text found on page {page_num + 1}, attempting OCR")
                try:
                    zoom = ocr_dpi / 72
                    # Use get_pixmap() which is the correct method
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))  # type: ignore
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                    # Apply basic enhancements (deskewing requires enhanced_ocr engine)
                    img = _enhance_image_for_ocr(img)

                    text = pytesseract.image_to_string(
                        img, lang=ocr_lang, config=f"--psm {ocr_psm} --oem {ocr_oem}"
                    )
                    if text.strip():
                        ocr_used = True
                        paragraphs = _process_paragraphs(text)
                        md_lines.extend(f"{para}\n\n" for para in paragraphs)
                        md_lines.append("*Text extracted using OCR technology*\n\n")
                    else:
                        empty_pages += 1
                        md_lines.append(
                            "*No text could be extracted from this page, even with OCR.*\n\n"
                        )
                except Exception as ocr_error:
                    logger.exception(f"OCR error on page {page_num + 1}")
                    empty_pages += 1
                    md_lines.append(
                        f"*OCR processing error on this page: {ocr_error}*\n\n"
                    )
            elif text.strip():
                paragraphs = _process_paragraphs(text)
                md_lines.extend(f"{para}\n\n" for para in paragraphs)
            else:
                empty_pages += 1
                md_lines.append("*No extractable text found on this page.*\n\n")

            if page_num < pdf_document.page_count - 1:
                md_lines.append("---\n\n")  # Page separator

        # Add summary notes
        if empty_pages > 0:
            note = f"*Note: {empty_pages} out of {pdf_document.page_count} pages had no extractable text{', even with OCR' if ocr_available else ''}.*\n\n"
            md_lines.insert(1, note)  # Insert after title
        if ocr_used:
            ocr_note = "*Note: OCR was used. Results may contain errors.*\n\n"
            md_lines.insert(1, ocr_note)

        pdf_document.close()
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write("".join(md_lines))

        logger.info(f"PDF converted to Markdown: {output_path}")
        return output_path
    except Exception as e:
        logger.exception("Error during PDF to Markdown conversion")
        raise RuntimeError(f"Error converting PDF to Markdown: {e}") from e


# --- Functions for specific engines --- #


def convert_pdf_to_md_with_ocr(
    input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
) -> Path:
    """
    Convert a PDF file to Markdown using OCR for pages with no extractable text.
    (Essentially calls convert_pdf_to_md with auto_ocr=True implicitly)
    """
    logger.info("Using standard OCR engine for PDF to Markdown.")
    # Ensures auto_ocr is treated as true for this function
    kwargs["auto_ocr"] = True
    return convert_pdf_to_md(input_path, output_path, **kwargs)


def convert_pdf_to_md_with_enhanced_ocr(
    input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
) -> Path:
    """
    Convert PDF to Markdown with advanced OCR techniques (deskewing, full preprocessing).
    """
    if fitz is None:
        logger.error("PyMuPDF is required.")
        raise ImportError("PyMuPDF is required.")
    if not TESSERACT_AVAILABLE:
        logger.error("Tesseract is required for enhanced OCR.")
        raise ImportError("Tesseract is required.")
    if not OPENCV_AVAILABLE:
        logger.warning(
            "OpenCV not found. Enhanced image preprocessing will be limited."
        )

    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        logger.error(f"Invalid input file type: {input_path.suffix}")
        raise ValueError(f"Input file must be a PDF: {input_path}")

    output_path = (
        Path(output_path).resolve() if output_path else input_path.with_suffix(".md")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config = ConfigManager()
    settings = config.get_converter_config("pdf2md")
    lang = kwargs.get("lang", settings.get("ocr_languages", "eng"))
    dpi = kwargs.get("dpi", settings.get("ocr_dpi", 300))
    force_ocr = kwargs.get("force_ocr", settings.get("force_ocr", False))
    psm = kwargs.get("psm", settings.get("ocr_psm", 1))
    oem = kwargs.get("oem", settings.get("ocr_oem", 3))

    logger.info(
        f"Converting {input_path} to Markdown with Enhanced OCR (lang={lang}, dpi={dpi})"
    )
    try:
        pdf_document = fitz.open(str(input_path))
        md_lines = [f"# {input_path.stem}\n\n"]
        empty_pages = 0
        ocr_used_pages = 0

        if pdf_document.is_encrypted:
            logger.warning("PDF is encrypted. Authentication may be required.")
            try:
                pdf_document.authenticate("")
            except Exception as auth_e:
                logger.error(f"Failed to authenticate encrypted PDF: {auth_e}")
                md_lines.append("*Error: Failed to authenticate encrypted PDF.*\n\n")

        for page_num in range(pdf_document.page_count):
            logger.debug(f"Processing page {page_num + 1} with enhanced OCR")
            page = pdf_document.load_page(page_num)
            text = "" if force_ocr else _extract_text_from_page(page)
            md_lines.append(f"## Page {page_num + 1}\n\n")

            if not text.strip() or force_ocr:
                logger.info(f"Using enhanced OCR on page {page_num + 1}")
                try:
                    zoom = dpi / 72
                    # Use get_pixmap() - fixed linter error
                    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))  # type: ignore
                    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                    # Full preprocessing pipeline
                    img = _deskew_image(img)  # Deskew first
                    img = _enhance_image_for_ocr(img)  # Then enhance

                    text = pytesseract.image_to_string(
                        img, lang=lang, config=f"--psm {psm} --oem {oem}"
                    )
                    if text.strip():
                        ocr_used_pages += 1
                        paragraphs = _process_paragraphs(text)
                        md_lines.extend(f"{para}\n\n" for para in paragraphs)
                        md_lines.append(
                            "*Text extracted using enhanced OCR technology*\n\n"
                        )
                    else:
                        empty_pages += 1
                        md_lines.append(
                            "*No text could be extracted from this page, even with enhanced OCR.*\n\n"
                        )
                except Exception as ocr_error:
                    logger.exception(f"Enhanced OCR error on page {page_num + 1}")
                    empty_pages += 1
                    md_lines.append(
                        f"*Enhanced OCR processing error on this page: {ocr_error}*\n\n"
                    )
            else:
                paragraphs = _process_paragraphs(text)
                md_lines.extend(f"{para}\n\n" for para in paragraphs)

            if page_num < pdf_document.page_count - 1:
                md_lines.append("---\n\n")

        # Add summary notes
        if empty_pages > 0:
            note = f"*Note: {empty_pages} out of {pdf_document.page_count} pages had no extractable text, even with enhanced OCR.*\n\n"
            md_lines.insert(1, note)
        if ocr_used_pages > 0:
            ocr_note = f"*Note: Enhanced OCR was used on {ocr_used_pages} pages. Results may contain errors.*\n\n"
            md_lines.insert(1, ocr_note)

        pdf_document.close()
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write("".join(md_lines))

        logger.info(f"PDF converted to Markdown with enhanced OCR: {output_path}")
        return output_path
    except Exception as e:
        logger.exception("Error during PDF to Markdown conversion with enhanced OCR")
        raise RuntimeError(f"Error converting PDF to Markdown: {e}") from e


def convert_pdf_to_md_with_pymupdf4llm(
    input_path: str | Path, output_path: str | Path | None = None, **kwargs: Any
) -> Path:
    """
    Convert a PDF file to Markdown using PyMuPDF4LLM.
    """
    if not PYMUPDF4LLM_AVAILABLE:
        logger.error("PyMuPDF4LLM is required for this engine.")
        raise ImportError("PyMuPDF4LLM is required.")

    input_path = Path(input_path).resolve()
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        logger.error(f"Invalid input file type: {input_path.suffix}")
        raise ValueError(f"Input file must be a PDF: {input_path}")

    output_path = (
        Path(output_path).resolve() if output_path else input_path.with_suffix(".md")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting {input_path} to Markdown using PyMuPDF4LLM")
    try:
        # PyMuPDF4LLM might have its own options, pass kwargs if needed
        markdown_text = parse_pdf_to_markdown(str(input_path), **kwargs)
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown_text)
        logger.info(f"PDF converted to Markdown (PyMuPDF4LLM): {output_path}")
        return output_path
    except Exception as e:
        logger.exception("Error during PDF to Markdown conversion using PyMuPDF4LLM")
        raise RuntimeError(f"Error converting PDF to Markdown: {e}") from e
