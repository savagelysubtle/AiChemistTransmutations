OCR Functionality in MDtoPDF
==========================

MDtoPDF now includes OCR (Optical Character Recognition) support, which allows you to extract text from scanned PDF documents and convert them to Markdown format.

Introduction
-----------

Many PDF documents, especially scanned documents, contain text as images rather than searchable text. The OCR functionality in MDtoPDF addresses this limitation by using Tesseract OCR to extract text from these images.

Prerequisites
------------

To use the OCR functionality, you'll need:

1. The pytesseract and Pillow Python packages (installed automatically with MDtoPDF)
2. Tesseract OCR installed on your system:

   - **Windows**: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - **MacOS**: ``brew install tesseract``
   - **Linux**: ``sudo apt-get install tesseract-ocr``

3. (Optional) Language data files for languages other than English:

   - **Windows**: Download language data files from the Tesseract GitHub repository
   - **MacOS**: ``brew install tesseract-lang``
   - **Linux**: ``sudo apt-get install tesseract-ocr-[lang]`` (replace [lang] with language code)

Usage
-----

Automatic OCR
~~~~~~~~~~~~

The standard ``convert_pdf_to_md`` function now includes automatic OCR detection, which will apply OCR only to pages that need it:

.. code-block:: python

    from mdtopdf.converters import convert_pdf_to_md

    # OCR is enabled by default and will be applied automatically when needed
    convert_pdf_to_md("input.pdf", "output.md")

    # To disable automatic OCR
    convert_pdf_to_md("input.pdf", "output.md", auto_ocr=False)

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~

Basic usage with default settings (English language, 300 DPI):

.. code-block:: bash

    python -m mdtopdf.cli --type pdf2md --input input.pdf --output output.md --ocr

Specifying a different language (e.g., French):

.. code-block:: bash

    python -m mdtopdf.cli --type pdf2md --input input.pdf --output output.md --ocr --ocr-lang fra

Specifying multiple languages (e.g., English and French):

.. code-block:: bash

    python -m mdtopdf.cli --type pdf2md --input input.pdf --output output.md --ocr --ocr-lang eng+fra

Setting a custom DPI (dots per inch) for better OCR quality:

.. code-block:: bash

    python -m mdtopdf.cli --type pdf2md --input input.pdf --output output.md --ocr --ocr-dpi 400

Python API - Specialized OCR Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For cases requiring more control over the OCR process, specialized functions are available:

.. code-block:: python

    from mdtopdf.converters import (
        convert_pdf_to_md_with_ocr,
        convert_pdf_to_md_with_enhanced_ocr,
        convert_pdf_to_md_with_pymupdf4llm
    )

    # Basic OCR
    convert_pdf_to_md_with_ocr("input.pdf", "output.md")

    # Enhanced OCR with better preprocessing
    convert_pdf_to_md_with_enhanced_ocr("input.pdf", "output.md", lang="fra", dpi=400)

    # Using PyMuPDF4LLM for specialized text extraction
    convert_pdf_to_md_with_pymupdf4llm("input.pdf", "output.md")

Batch Processing with OCR
~~~~~~~~~~~~~~~~~~~~~~~~

The MDtoPDF package includes a batch processing script that can convert multiple PDF files with automatic OCR:

.. code-block:: bash

    python batch_convert_pdf_to_md.py path/to/pdf_directory

For more information on batch processing capabilities, see :doc:`usage/batch_conversion`.

How It Works
-----------

The OCR-enabled PDF to Markdown conversion works as follows:

1. The converter attempts to extract text from each page using PyMuPDF's normal extraction methods
2. If a page contains no extractable text (or very little text), it's considered a scanned image
3. For scanned images, the page is rendered to a high-resolution image
4. Image preprocessing is applied to enhance text clarity (contrast adjustment, noise removal)
5. Tesseract OCR processes the enhanced image to extract text
6. The extracted text is formatted as Markdown
7. The results are combined into a single Markdown file

Configuration Options
--------------------

Language
~~~~~~~~

Tesseract OCR supports many languages. You can specify the language of your document using ISO 639-2 language codes:

- ``eng``: English (default)
- ``fra``: French
- ``deu``: German
- ``spa``: Spanish
- ``ita``: Italian
- ``rus``: Russian
- ``chi_sim``: Simplified Chinese
- ``chi_tra``: Traditional Chinese
- ``jpn``: Japanese
- ``kor``: Korean

For a complete list of supported languages, see the `Tesseract documentation <https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html>`_.

DPI (Dots Per Inch)
~~~~~~~~~~~~~~~~~~

The DPI setting controls the resolution of the images created for OCR processing:

- Lower DPI (e.g., 150): Faster processing, but potentially lower accuracy
- Medium DPI (300, default): Good balance between speed and accuracy
- Higher DPI (e.g., 600): Better accuracy for small text, but slower processing and higher memory usage

Text Extraction Threshold
~~~~~~~~~~~~~~~~~~~~~~~

By default, the converter uses OCR for a page if less than 10 characters are extracted using traditional methods. This threshold can be adjusted in the API:

.. code-block:: python

    convert_pdf_to_md_with_ocr("input.pdf", "output.md", text_threshold=50)

Advanced Usage
-------------

Combining with PyMuPDF4LLM
~~~~~~~~~~~~~~~~~~~~~~~~~

For specialized use cases like preparing text for Large Language Models (LLMs), you can use the PyMuPDF4LLM-enhanced conversion:

.. code-block:: bash

    python -m mdtopdf.cli --type pdf2md --input input.pdf --output output.md --use-pymupdf4llm

Custom Tesseract Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Advanced users can customize Tesseract OCR settings by creating a configuration file and passing the path:

.. code-block:: python

    from mdtopdf import convert_pdf_to_md_with_ocr

    convert_pdf_to_md_with_ocr(
        "input.pdf",
        "output.md",
        lang="eng",
        dpi=300,
        tesseract_config="custom_tesseract_config.txt"
    )

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~~

1. **Tesseract not found**: Ensure Tesseract is installed and in your system PATH
2. **OCR quality is poor**: Try increasing the DPI or using a different language setting
3. **Process is very slow**: Reduce the DPI or limit the number of pages being processed
4. **"Import pytesseract could not be resolved"**: Install the pytesseract package and ensure Tesseract is properly installed

Debug Logging
~~~~~~~~~~~~

To enable debug logging for OCR operations:

.. code-block:: python

    import logging
    logging.basicConfig(level=logging.DEBUG)

    from mdtopdf import convert_pdf_to_md
    convert_pdf_to_md("input.pdf", "output.md")

Performance Tips
--------------

- For large documents, consider processing only specific page ranges
- Setting the appropriate language dramatically improves OCR accuracy
- For multilingual documents, specify all relevant languages (e.g., "eng+fra+deu")
- Higher DPI settings may improve quality but require more memory and processing time
- Use the batch processing functionality with multiple worker processes for converting large collections of documents