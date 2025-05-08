\
Usage
=====

This section explains how to use the Aichemist Transmutation Codex, covering both the Command-Line Interface (CLI) and the Graphical User Interface (GUI).

Command-Line Interface (CLI)
----------------------------

The CLI is the primary way to interact with the Aichemist Transmutation Codex for scripting and automated workflows. The main command is `transmute`.

Basic Syntax
~~~~~~~~~~~~

.. code-block:: console

   transmute [CONVERSION_TYPE] [OPTIONS] --input-files <file1> [<file2> ...] --output-dir <directory>

Key Arguments:
~~~~~~~~~~~~~~

*   `CONVERSION_TYPE`: Specifies the type of conversion to perform. Examples:
    *   `pdf2md`: PDF to Markdown
    *   `md2pdf`: Markdown to PDF
    *   `html2pdf`: HTML to PDF
    *   `md2html`: Markdown to HTML
    *   `pdf2html`: PDF to HTML
    *   `docx2md`: DOCX to Markdown
    (Run `transmute --help` for a full list of available conversion types.)

*   `--input-files <file1> [<file2> ...]` or `-i <file1> [<file2> ...]`: (Required) One or more input files to convert.
*   `--output-dir <directory>` or `-o <directory>`: (Optional) Directory where the converted files will be saved. If not provided, output files are typically saved in the same directory as their respective input files or in a predefined output subfolder.

Common Options:
~~~~~~~~~~~~~~~

*   `--help`: Show the help message and exit.
*   `--version`: Show the version of the Aichemist Transmutation Codex.
*   `--verbose` or `-v`: Enable verbose output for more detailed logging.
*   `--progress`: Show a progress bar during conversion (if applicable).
*   Specific conversion types may have their own options (e.g., `--ocr-language <lang>` for `pdf2md`, `--engine <name>` for `md2pdf`). Use `transmute [CONVERSION_TYPE] --help` to see options for a specific converter.

Examples:
~~~~~~~~

1.  **Convert a single PDF to Markdown**:

    .. code-block:: console

       transmute pdf2md --input-files document.pdf

2.  **Convert multiple Markdown files to PDF and specify an output directory**:

    .. code-block:: console

       transmute md2pdf --input-files chapter1.md notes.md --output-dir ./converted_pdfs

3.  **Convert an HTML file to PDF using a specific engine**:

    .. code-block:: console

       transmute html2pdf --input-files report.html --engine weasyprint

4.  **Convert a PDF to Markdown using OCR for scanned pages (specifying language)**:

    .. code-block:: console

       transmute pdf2md --input-files scanned_doc.pdf --ocr-language eng+fra

Graphical User Interface (GUI)
------------------------------

The Aichemist Transmutation Codex also provides a user-friendly GUI for easy drag-and-drop conversions and batch processing.

Launching the GUI:
~~~~~~~~~~~~~~~~~~

*   If you installed via a pre-built package or installer, there should be a desktop shortcut or an entry in your applications menu.
*   If you installed from source, you might have a script like `run-gui.bat` or you can typically run it from the project root using a command like:

    .. code-block:: console

       npm run gui # (or similar, check your project's package.json)

Key Features of the GUI:
~~~~~~~~~~~~~~~~~~~~~~~~

1.  **File Selection**:
    *   Drag and drop one or more files onto the application window.
    *   Click a "Select Files" or "Add Files" button to open a native file dialog.

2.  **Conversion Type Selection**:
    *   Choose the input format (often auto-detected) and the desired output format from dropdown menus.

3.  **Output Configuration**:
    *   Specify an output directory for all converted files.
    *   Option to save in the same directory as input files or a dedicated subfolder.

4.  **Conversion Options**:
    *   Relevant options for the selected conversion type will be displayed (e.g., OCR language, PDF engine choice).

5.  **Starting Conversion**:
    *   Click a "Start Conversion" or "Transmute" button.

6.  **Progress and Status**:
    *   An overall progress bar for batch conversions.
    *   Individual status for each file (e.g., pending, processing, success, failed).
    *   Detailed logs or messages for any errors encountered.

7.  **Results**:
    *   Notification upon completion.
    *   Option to open the output directory or individual files directly.

(Please refer to the :doc:`architecture/project_brief_gui` for more detailed information on the GUI design and features.)

Using as a Python Library
-------------------------

The core conversion logic of the Aichemist Transmutation Codex can also be used directly in your Python scripts.

Example (Conceptual):
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aichemist_transmutation_codex import transmute_file
   from pathlib import Path

   try:
       input_file = Path("path/to/your/document.md")
       output_directory = Path("path/to/output_location/")
       output_directory.mkdir(parents=True, exist_ok=True)

       # Define conversion type and options
       conversion_type = "md2pdf"
       options = {"engine": "weasyprint"}

       result_path = transmute_file(
           conversion_type=conversion_type,
           input_file=input_file,
           output_dir=output_directory,
           options=options
       )
       print(f"Successfully converted to: {result_path}")

   except FileNotFoundError:
       print(f"Error: Input file not found at {input_file}")
   except Exception as e:
       print(f"An error occurred: {e}")

For detailed API usage, please refer to the :doc:`api/modules` documentation.