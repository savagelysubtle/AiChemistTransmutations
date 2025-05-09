.. automodule:: aichemist_transmutation_codex.merger.pdf_merger
    :noindex:

PDF Merging
===========

The Aichemist Transmutation Codex provides a feature to merge multiple PDF documents into a single PDF file. This functionality is accessible through the main graphical user interface (GUI) and is also available as a Python function for programmatic use.

GUI Usage
---------

In the application's GUI:

1.  Select "Merge PDFs to Single PDF" from the conversion type dropdown.
2.  Select two or more PDF files you wish to merge using the "Select PDFs to Merge (Min. 2)" button.
3.  The "Merge Options" section will appear, allowing you to:
    *   Reorder the selected PDF files. The order shown (top to bottom) will be the order they appear in the merged document.
    *   Remove any unwanted files from the list.
    *   Specify a name for the output merged PDF file (e.g., "combined_report.pdf").
4.  Select an output directory where the merged PDF will be saved. This is **required** for merging.
5.  Click "Run Conversion" to start the merging process.

The merged PDF will be saved in the chosen output directory with the specified filename.

Python API
----------

The core functionality for merging PDFs is provided by the ``merge_multiple_pdfs_to_single_pdf`` function located in the ``aichemist_transmutation_codex.merger.pdf_merger`` module.

.. autofunction:: merge_multiple_pdfs_to_single_pdf

**Example from Docstring (for illustration):**

The function's own docstring (which `autofunction` will render above) contains a runnable example. Here it is for quick reference, though the directive will present it formatted by Sphinx:

.. code-block:: python
   :caption: Merging PDFs Programmatically

   from pathlib import Path
   # Assuming the module is accessible, e.g., if your script is in the project root
   # or the package is installed.
   from aichemist_transmutation_codex.merger.pdf_merger import merge_multiple_pdfs_to_single_pdf

   # Create dummy PDF files for example
   from PyPDF2 import PdfWriter

   try:
       temp_dir = Path("temp_merge_example")
       temp_dir.mkdir(exist_ok=True)
       pdf1_path = temp_dir / "doc1.pdf"
       pdf2_path = temp_dir / "doc2.pdf"
       output_path = temp_dir / "merged_final.pdf"

       writer1 = PdfWriter()
       writer1.add_blank_page(width=210, height=297)
       with open(pdf1_path, "wb") as f1:
           writer1.write(f1)

       writer2 = PdfWriter()
       writer2.add_blank_page(width=210, height=297)
       with open(pdf2_path, "wb") as f2:
           writer2.write(f2)

       input_files = [pdf1_path, pdf2_path]
       merged_file_path = merge_multiple_pdfs_to_single_pdf(
           input_paths=input_files,
           output_path=output_path
       )
       print(f"Successfully merged PDFs into: {merged_file_path}")

   except Exception as e:
       print(f"An error occurred: {e}")
   finally:
       # Clean up
       import shutil
       if temp_dir.exists():
           shutil.rmtree(temp_dir)

.. note::
   For the ``autofunction`` directive to work correctly, Sphinx must be configured to find your Python modules (typically by setting `sys.path` in `conf.py` or ensuring the package is installed in the environment where Sphinx builds the documentation). The `.. automodule:: ... :noindex:` line at the top helps Sphinx locate the function without adding the module itself to the general index if not desired.

Considerations
--------------

*   **File Order**: The order in which PDF files are provided (either in the GUI list or the Python `input_paths` list) determines their sequence in the final merged document.
*   **Error Handling**: The merger function includes checks for file existence, valid PDF formats, and a minimum of two input files. Errors will be logged and raised as exceptions.
*   **Dependencies**: This feature relies on the `PyPDF2` library.