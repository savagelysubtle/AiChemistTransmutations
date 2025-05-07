Editable PDF Workflow & Library Research
======================================

.. contents:: Table of Contents
   :local:
   :depth: 2

Introduction
------------
The ability to *edit* Portable Document Format (PDF) files programmatically—adding or modifying text, images, form fields, annotations, or converting a PDF into another editable format (e.g. **DOCX**) and back—is an advanced requirement that goes beyond simple PDF generation.

This research document compares popular **Python** libraries (and a few notable commercial SDKs) that enable:

1. Direct creation of **interactive/editable** PDF files (form fields, annotations, JavaScript actions, etc.).
2. **Post-processing** existing PDFs—merging, splitting, rotating pages, updating metadata, encrypting/decrypting.
3. **Round-trip editing**: converting PDF → editable format (e.g. DOCX / HTML) → PDF.

The goal is to inform future converter modules that comply with :doc:`800-feature-development <../architecture/800-feature-development>` and :doc:`801-pdf-converter-development <../architecture/801-pdf-converter-development>` guidelines.

Quick-Look Comparison Matrix
---------------------------

+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| Library / SDK  | Licence & Cost      | Editable PDF? | Form Fields? |  PDF→DOCX?  | Notes                        |
+================+======================+===============+==============+=============+=============================+
| **ReportLab**  | BSD-style (open)     | Yes (canvas)  | Limited      | No          | Industry-standard generator. |
|                | Commercial support   |               | (AcroForm)   |             | Excellent for custom layout. |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **borb**       | AGPL-3  (free)       | Yes           | Yes          | No          | Modern, high-level API;      |
|                | Commercial licence   |               |              |             | supports digital signatures. |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **pypdf**      | BSD-2 (open)         | Partial*      | Read/Write   | No          | Successor of PyPDF2; great   |
|                |                      |               |              |             | for merging, stamping.       |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **PyMuPDF**    | GPL-3 / commercial   | Yes           | No           | *Yes*       | Fast rendering, text         |
| (**fitz**)     |                      | (page objects) |              | (extract    | extraction; can export pages |
|                |                      |               |              |   images)   | to HTML, DOCX via `get_text`.|
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **pdf2docx**   | MIT (open)           | N/A           | N/A          | Yes         | Bidirectional DOCX converter |
|                |                      |               |              |             | (layout may vary).           |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **docx2pdf**   | MIT (open)           | N/A           | N/A          | No          | Wrapper around MS Word /     |
|                |                      |               |              |             | macOS/LibreOffice printers;  |
|                |                      |               |              |             | ideal for DOCX → PDF.        |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **pdfforms**   | LGPL-3 (open)        | No            | **Yes**      | No          | Simple AcroForm filler;      |
|                |                      |               |              |             | no field creation.           |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **PyPDFForm**  | MIT (open)           | No            | **Yes** (rich)| No         | Declarative data-binding for |
|                |                      |               |               |            | existing templates.          |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **Aspose.PDF** | Commercial (closed)  | **Yes**       | **Yes**      | **Yes**     | Broad feature set, but paid. |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+
| **ironpdf**    | Commercial (closed)  | **Yes**       | **Yes**      | *Limited*   | .NET native, Python wrapper. |
+----------------+----------------------+---------------+--------------+-------------+-----------------------------+

\* *pypdf* can **modify** existing objects (e.g., add blank pages, merge, update form data) but **cannot** draw arbitrary graphics from scratch without external helpers.

Detailed Library Notes
----------------------

ReportLab
~~~~~~~~~
* **Strengths**: Mature, performant; fine-grained canvas API; supports *static* AcroForms, digital signatures, PDF/A.
* **Weaknesses**: Creating complex interactive forms programmatically is verbose. Not focused on PDF → other formats.
* **Ideal For**: Generator modules (Markdown → PDF, HTML → PDF) where we control the entire layout.

borb
~~~~
* **Strengths**: High-level API for tables, paragraphs, charts, **form field creation**, JavaScript actions, encryption.
* **Weaknesses**: AGPL may require open-sourcing our code or acquiring a commercial licence; community still growing.
* **Ideal For**: Future modules that need rich interactive PDFs (e.g., invoice forms, survey PDFs).

pypdf (successor of PyPDF2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~
* **Strengths**: Pure-Python, no C deps; merge, split, rotate, **read/write AcroForm data**; incremental saves.
* **Weaknesses**: Cannot create new drawing content without helper libs; form field *creation* is experimental.
* **Ideal For**: Post-processing, watermarking, filling existing templates.

PyMuPDF (fitz)
~~~~~~~~~~~~~~
* **Strengths**: Fast C++ core; extract images, text, **convert pages to DOCX/HTML** (`page.get_text("html")`), draw graphics.
* **Weaknesses**: GPL/commercial; no built-in DOCX *import*; editing form fields limited.
* **Round-Trip Strategy**: `pdf` → *html*/*docx* (edit externally) → regenerate PDF (via `docx2pdf` or HTML → PDF converter).

pdf2docx + docx2pdf Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``pdf2docx`` converts a PDF page-by-page into a DOCX document, preserving paragraphs and images as best as possible.
The resulting DOCX can be edited in Microsoft Word, then reconverted to PDF via ``docx2pdf`` (which relies on Word or
LibreOffice). **Caveats**:

* Complex vector graphics become raster images.
* Table detection is heuristic; multi-column layouts may break.
* Fonts/subsets might not round-trip perfectly.

PyPDFForm / pdfforms
~~~~~~~~~~~~~~~~~~~~
If the workflow involves *existing* PDF templates with AcroForm fields, these libraries allow **data binding** to populate
fields (text, checkboxes, radio buttons) and *optionally flatten* the form afterwards.

Commercial SDKs (Aspose.PDF, ironpdf)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Commercial libraries provide enterprise-grade features—OCR, redaction, comparison, linearization—but at a cost.
They may be justified for **WYSIWYG** fidelity requirements or advanced digital signing.

Recommended Stack for This Project
----------------------------------

Based on project constraints (open-source preference, Windows platform, Python 3.13, licence compatibility), the
following tiered approach is proposed:

1. **Lightweight editing / form filling of existing PDFs** → ``pypdf`` (BSD-2) plus helper utilities.
2. **Interactive PDF generation (new converter)** → ``borb`` (AGPL) *or* ``ReportLab`` for OSS-only deployments.
3. **Round-trip editable workflow** (PDF ⇄ DOCX):

   * **Convert PDF → DOCX**: ``pdf2docx`` (MIT).
   * **User edits DOCX** in MS Word.
   * **Convert DOCX → PDF**: ``docx2pdf`` (MIT) via installed Word *or* LibreOffice.

   This could be wrapped in a **Python batch helper** exposed through the Electron UI.

Prototype Converter Namespaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* ``src/mdtopdf/converters/pdf_edit.py`` – helper functions based on **pypdf** for merging, form filling, and stamping.
* ``src/mdtopdf/converters/pdf_to_docx.py`` – wraps **pdf2docx**.
* ``src/mdtopdf/converters/docx_to_pdf.py`` – wraps **docx2pdf**.

Next Steps
----------

1. **Spike Tests** – Create POCs measuring fidelity & performance for:

   * ``pdf2docx`` conversion accuracy with sample invoices.
   * Form field creation with ``borb`` vs ``ReportLab``.

2. **Dependency Impact** – AGPL obligations for ``borb``; if unacceptable, limit to **ReportLab + pypdf** blend.
3. **Design Converter APIs** – Follow templates in :doc:`801-pdf-converter-development <../architecture/801-pdf-converter-development>`.
4. **Unit Tests** – Draft pytest cases under ``tests/unit/test_converters/`` focusing on:

   * PDF → DOCX layout assertions.
   * Successful form fill & flatten operations.

5. **GUI Flow** – Extend **electron_bridge.py** to expose *"Edit PDF"* flow in React UI with real-time progress.

References & Further Reading
----------------------------

* *Real Python* – `Create and Modify PDF Files in Python <https://realpython.com/creating-modifying-pdf/>`_
* borb documentation – https://github.com/jorisschellekens/borb
* pypdf cookbook – https://pypdf.readthedocs.io/en/latest/user/cookbook.html
* pdf2docx – https://pypi.org/project/pdf2docx/
* docx2pdf – https://pypi.org/project/docx2pdf/
* ReportLab User Guide – https://www.reportlab.com/docs/reportlab-userguide.pdf

Enhancing PDF Editability for Adobe Acrobat
-------------------------------------------

While many libraries can *generate* PDFs, ensuring a high degree of editability directly within Adobe Acrobat (Pro/DC) often means focusing on two main areas: well-structured content and proper use of PDF features like AcroForms.

1.  **AcroForms for Data Entry and Simple Edits**:
    For PDFs that require users to fill in data (text fields, checkboxes, radio buttons, dropdowns), creating them with AcroForm fields is the most robust approach. Adobe Acrobat excels at working with these forms.
    *   **Libraries for Creation**: `borb` and `ReportLab` can be used to programmatically define AcroForm fields during PDF generation.
    *   **Libraries for Filling**: `pypdf` and `PyPDFForm` can populate or read data from existing AcroForms.
    When such a PDF is opened in Acrobat, the form fields are interactive, and users can typically save their changes (either as a filled form or a flattened PDF, depending on Acrobat's settings and user actions).

2.  **Content and Layout Editing (Round-Trip via DOCX)**:
    For more substantial edits to the base content of a PDF (e.g., modifying paragraphs, restructuring layouts, changing embedded images), Adobe Acrobat's advanced editing tools are powerful. However, programmatically creating a PDF that is *natively* as editable as a source document (like a Word file) is challenging.
    *   The **PDF → DOCX → PDF round-trip workflow** discussed earlier (using `pdf2docx` and `docx2pdf`) is a practical way to achieve deep editability. Users can take the DOCX output, edit it extensively in Microsoft Word (or a compatible editor), and then either:
        *   Save it as a PDF directly from Word.
        *   Use Acrobat to convert the edited DOCX back to PDF.
        *   Use our `docx2pdf` converter to bring it back to PDF.
    This approach leverages the mature editing capabilities of word processors.

3.  **PDF Structure and Standards**:
    *   Adhering to PDF standards (e.g., PDF/A for archiving, PDF/UA for accessibility) can sometimes influence how well Acrobat interprets and handles a document, though direct editability is more about content structure.
    *   Ensuring fonts are embedded correctly is crucial for consistent appearance and editability of text content.

For this project, providing options to generate PDFs with clear AcroForm fields and facilitating the PDF ⇄ DOCX conversion will offer users good flexibility for editing in Adobe Acrobat.

Conceptualizing a Basic GUI PDF Editor Extension
------------------------------------------------

To provide users with direct, albeit basic, PDF editing capabilities within the application, we can conceptualize an extension to the existing Electron/React/TypeScript GUI. This would not aim to replicate advanced features of tools like Adobe Acrobat but would offer convenience for common tasks.

**Core Architecture & Technologies**:

*   **Environment**: Electron (Host), React (UI Framework), TypeScript (Language).
*   **PDF Rendering**: `PDF.js` (by Mozilla) is a robust library for rendering PDF documents in the browser and thus in Electron. The `react-pdf` wrapper can simplify its integration into React components.
*   **PDF Manipulation (Client-Side)**: `pdf-lib` is a strong candidate. It's written in TypeScript, compiles to pure JavaScript, has no native dependencies, and works in browser/Node environments. It allows for:
    *   Adding text, images, and vector graphics.
    *   Creating and filling PDF form fields.
    *   Modifying existing PDF pages (e.g., adding content, drawing).
    *   Saving modified PDFs.
*   **Python Backend Interaction**: For more complex operations or to ensure consistency with other Python-based converters, the Electron frontend can communicate with the Python backend (`electron_bridge.py`) via IPC.

**Key Features for a Basic Editor**:

1.  **Load & Display PDF**:
    *   User selects a PDF file.
    *   The PDF is loaded and rendered page by page in a dedicated React component using `PDF.js` / `react-pdf`.
2.  **Basic Annotations**:
    *   **Add Text**: Allow users to click on the PDF and type text. The text's font, size, and color could be basic options.
    *   **Simple Shapes**: Drawing basic shapes like rectangles or lines (e.g., for highlighting or underlining).
    *   **Freehand Drawing**: A simple pen tool.
3.  **Form Field Interaction**:
    *   If the loaded PDF contains AcroForm fields, allow users to fill them.
    *   Potentially allow adding new, simple form fields (though this adds complexity).
4.  **Saving Modifications**:
    *   **Client-Side Save**: `pdf-lib` can apply the annotations/changes directly to the PDF byte stream on the client-side and offer it for download/save.
    *   **Server-Side Save (Optional)**: For consistency or more complex merging, the frontend could send annotation data (e.g., type, position, content) to the Python backend, which then uses a Python PDF library (like `pypdf` or `borb`) to apply these changes and save the file.

**High-Level Workflow Example (Adding Text Annotation)**:

1.  User opens a PDF in the GUI editor.
2.  The PDF is rendered using `react-pdf`.
3.  User selects the "Add Text" tool from a toolbar.
4.  User clicks on the rendered PDF page; a text input appears.
5.  User types text and confirms.
6.  The React component managing the editor captures the text content, position, and basic styling.
7.  When the user clicks "Save":
    *   The application uses `pdf-lib` to load the original PDF's bytes.
    *   It then iterates through the collected annotations (like the new text) and uses `pdf-lib` methods (e.g., `page.drawText()`) to add them to the appropriate pages.
    *   `pdf-lib` generates the new PDF byte array.
    *   Electron's main process is invoked to save these bytes to a new file or overwrite the original (with user confirmation).

**Potential Challenges**:

*   **Complexity of PDF Specification**: Even basic modifications require careful handling of the PDF structure.
*   **Performance**: Rendering and manipulating large or complex PDFs entirely on the client-side can be performance-intensive. `PDF.js` is optimized, but real-world testing is needed.
*   **Annotation Management**: Keeping track of annotations, their properties, and ensuring they are correctly applied to the PDF requires a robust state management approach in React.
*   **Undo/Redo**: Implementing a reliable undo/redo system for editing operations adds significant complexity.
*   **Fidelity**: Ensuring that client-side modifications are rendered correctly across different PDF viewers.

**Integration with Project Rules**:

*   This feature would align with **Rule 800 (Feature Development)**, requiring phases for research, implementation (Python backend if needed, TypeScript/React frontend), testing (unit and manual GUI testing), and documentation.
*   Communication between Electron (TypeScript) and Python would follow guidelines in **Rule 811 (Electron Main/Preload)** and **Global Project Context (001)** regarding async functions and JSON messaging.

This GUI editor would be a significant feature. Starting with a very limited set of annotation tools (e.g., only adding text boxes) and iterating would be a sensible approach.

.. note::
   This document complies with :ref:`400-documentation-format` by using **reStructuredText** and residing under
   ``docs/source/development/``.