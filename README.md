# AiChemist Transmutation Codex

AiChemist Transmutation Codex is a Python library for converting between different document formats,
with a focus on Markdown and PDF conversions, intended as a core component of the AiChemist suite.

## Features

- Convert Markdown to PDF
- Convert Markdown to HTML
- Convert PDF to Markdown (with OCR support for scanned documents)
- Convert PDF to HTML
- Convert HTML to PDF
- Command-line interface
- GUI interface
- Electron bridge for integration with desktop applications

## Installation

```bash
pip install aichemist-transmutation-codex
```

### Dependencies for OCR

To use the OCR feature for scanned PDFs, you need to install Tesseract OCR:

- **Windows**: Download and install from
  https://github.com/UB-Mannheim/tesseract/wiki
- **MacOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Usage

### Command Line

```bash
# Convert Markdown to PDF
python -m aichemist_transmutation_codex.cli --type md2pdf --input input.md --output output.pdf

# Convert PDF to Markdown
python -m aichemist_transmutation_codex.cli --type pdf2md --input input.pdf --output output.md

# Convert PDF to Markdown with OCR (for scanned documents)
python -m aichemist_transmutation_codex.cli --type pdf2md --input input.pdf --output output.md --ocr

# Convert PDF to Markdown with OCR in a different language (e.g., French)
python -m aichemist_transmutation_codex.cli --type pdf2md --input input.pdf --output output.md --ocr --ocr-lang fra

# Convert PDF to Markdown with OCR at higher resolution
python -m aichemist_transmutation_codex.cli --type pdf2md --input input.pdf --output output.md --ocr --ocr-dpi 400

# Convert PDF to Markdown using PyMuPDF4LLM (optimized for LLM input)
python -m aichemist_transmutation_codex.cli --type pdf2md --input input.pdf --output output.md --use-pymupdf4llm
```

### GUI

```bash
# Launch the GUI
python -m aichemist_transmutation_codex.cli --gui
```

### Python API

```python
from aichemist_transmutation_codex import convert_md_to_pdf, convert_pdf_to_md

# Convert Markdown to PDF
convert_md_to_pdf("input.md", "output.pdf")

# Convert PDF to Markdown
convert_pdf_to_md("input.pdf", "output.md")

# Convert PDF to Markdown with OCR for scanned documents
from aichemist_transmutation_codex import convert_pdf_to_md_with_ocr
convert_pdf_to_md_with_ocr("input.pdf", "output.md", lang="eng", dpi=300)

# Convert PDF to Markdown with PyMuPDF4LLM (optimized for LLM input)
from aichemist_transmutation_codex import convert_pdf_to_md_with_pymupdf4llm
convert_pdf_to_md_with_pymupdf4llm("input.pdf", "output.md")
```

## OCR Support for Scanned PDFs

AiChemist Transmutation Codex now includes OCR (Optical Character Recognition) support for extracting
text from scanned PDF documents. This feature is particularly useful for PDFs
that are scanned images or documents without embedded text.

### How OCR Works

1. First, the converter attempts to extract text using PyMuPDF's built-in
   methods
2. If no text is found on a page, it's converted to an image and processed with
   Tesseract OCR
3. The extracted text is then formatted as Markdown

### OCR Options

- **Language** (`--ocr-lang`): Specify the language of the document. Default is
  English (`eng`).

  - For multiple languages, combine with `+` e.g., `eng+fra` for English and
    French
  - See
    [Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
    for language codes

- **DPI** (`--ocr-dpi`): Resolution for OCR scanning. Higher values may improve
  accuracy but use more memory. Default is 300.

### PyMuPDF4LLM for LLM-Optimized Conversion

For converting PDFs for use with Large Language Models (LLMs), AiChemist Transmutation Codex
integrates with PyMuPDF4LLM, which provides specialized Markdown output that
works well as input for LLMs.

To use this feature, install the PyMuPDF4LLM package:

```bash
pip install pymupdf4llm
```

## Development

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/aichemist-transmutation-codex.git # Assuming you'll rename the repo too
   cd aichemist-transmutation-codex
   ```

2. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for
details.
