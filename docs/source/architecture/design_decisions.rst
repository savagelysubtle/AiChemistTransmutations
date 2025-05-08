\
Design Decisions and Architectural Choices
======================================

This document outlines the key design decisions made for the Aichemist Transmutation Codex project and provides rationale for these choices.

1. Converter Architecture
------------------------

Decision: Plugin-based Converter System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've designed the converter system to be modular and plugin-based, with each format converter encapsulated in its own module.

**Rationale:**

- Enables easy addition of new output formats
- Promotes separation of concerns
- Makes testing individual converters simpler
- Allows for independent development and maintenance of each converter

Decision: Function-based vs Class-based API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've chosen a primarily function-based API for converters rather than a class hierarchy.

**Rationale:**

- Simpler for most use cases
- More Pythonic for operations that don't require state
- Easier for users to understand and use
- Reduces boilerplate code

2. Project Structure Decisions
-----------------------------

Decision: src-layout Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've adopted the src-layout pattern with a src/ directory containing the package code.

**Rationale:**

- Prevents accidental import of code from the development directory
- Creates a clear separation between package code and development/test code
- Ensures testing is done against the installed package
- Follows modern Python packaging best practices

Decision: Separation of CLI from Core Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command-line interface is kept separate from the core conversion logic.

**Rationale:**

- Allows the package to be used both as a library and as a command-line tool
- Facilitates testing of core functionality without CLI dependencies
- Makes it easier to create alternative interfaces (GUI, web service, etc.)

3. Technology Choices
--------------------

Decision: Build System - Use pyproject.toml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We're using pyproject.toml for package configuration rather than setup.py.

**Rationale:**

- Modern Python packaging standard (PEP 517/518)
- Cleaner separation of build requirements from runtime dependencies
- Single configuration file for multiple tools (black, isort, pytest, etc.)
- Better handling of development dependencies

Decision: Linting and Code Quality - Ruff
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've chosen Ruff as our primary linting and formatting tool.

**Rationale:**

- Much faster than alternatives like flake8, black, and isort combined
- Consolidates multiple tools into a single tool
- Extensive rule set covering style, bugs, and complexity
- Customizable to project needs

Decision: Type Checking - mypy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've chosen mypy for static type checking.

**Rationale:**

- Industry standard for Python type checking
- Well-documented and maintained
- Integrates with major IDEs and editors
- Gradual typing approach allows incremental adoption

4. Documentation Approach
------------------------

Decision: ReStructuredText-based Documentation with Sphinx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've chosen reStructuredText for our documentation format and Sphinx as our documentation generator.

**Rationale:**

- Sphinx is the de facto standard for Python project documentation
- reStructuredText provides excellent support for technical documentation
- Sphinx extensions like autodoc make API documentation easier
- Can generate multiple output formats (HTML, PDF, etc.)
- Integrates well with Read the Docs for hosting

Decision: Documentation in Code and Separate Docs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We maintain both docstrings in code and separate documentation files.

**Rationale:**

- Docstrings provide context where the code is used
- Separate docs allow for more comprehensive explanations
- Different documentation serves different audiences (users vs developers)
- Follows the principle of documentation at appropriate levels of detail

5. Testing Strategy
------------------

Decision: pytest as Testing Framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've chosen pytest as our testing framework.

**Rationale:**

- Rich feature set with fixtures, parameterization, and plugins
- Concise test syntax
- Strong community support
- Extensive plugin ecosystem

Decision: Separation of Unit and Integration Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We separate unit tests from integration tests in different directories.

**Rationale:**

- Allows running fast unit tests separately from slower integration tests
- Clarifies the scope and purpose of each test
- Makes it easier to set up CI/CD pipelines with different test strategies
- Helps in maintaining test coverage metrics separately

6. Dependency Management
-----------------------

Decision: Minimal External Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We strive to keep external dependencies to a minimum.

**Rationale:**

- Reduces potential security vulnerabilities
- Minimizes installation issues
- Decreases maintenance burden
- Improves long-term sustainability

Decision: Pinned Dependency Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We pin dependency versions in our configuration.

**Rationale:**

- Ensures reproducible builds
- Prevents unexpected breaking changes
- Makes testing more reliable
- Allows controlled upgrades with testing

7. Future Considerations
-----------------------

Potential Enhancement: Web Service API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We're considering adding a web service API in the future.

**Rationale:**

- Would enable integration with web applications
- Could provide online conversion capabilities
- Would expand the utility of the tool
- Aligns with modern trends in providing services

Potential Enhancement: GUI Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A graphical user interface could be added as a separate package.

**Rationale:**

- Would make the tool accessible to non-technical users
- Could provide preview capabilities
- Would keep the core package lightweight
- Separates concerns between CLI and GUI users

8. Rejected Alternatives
-----------------------

Rejected: Single Monolithic Converter Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We considered but rejected having a single Converter class handling all formats.

**Rationale for rejection:**

- Would become unwieldy as more formats are added
- Violates the Single Responsibility Principle
- Makes testing more complex
- Increases coupling between different format converters

Rejected: Complex Class Hierarchy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We considered but rejected having an abstract BaseConverter with subclasses.

**Rationale for rejection:**

- Unnecessary complexity for the current requirements
- Python's duck typing reduces the need for formal interfaces
- Function-based approach is simpler and more flexible
- Can refactor to this approach later if complexity increases

9. Converter Matrix and Implementation Status
--------------------------------------------

.. list-table:: Converter Modules, Libraries, and Status
   :header-rows: 1
   :widths: 15 15 35 25 10

   * - Input Format
     - Output Format
     - Module File
     - Library / Tool
     - Status
   * - DOCX
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/doc_to_markdown.py``
     - ``python-docx``, ``mammoth``
     - Completed
   * - Markdown (``.md``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/markdown_to_pdf.py``
     - ``markdown_pdf``
     - Completed
   * - HTML (``.html``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/html_to_pdf.py``
     - ``pdfkit`` (``wkhtmltopdf``)
     - Completed
   * - Markdown (``.md``)
     - HTML (``.html``)
     - ``src/aichemist_transmutation_codex/converters/markdown_to_html.py``
     - ``markdown`` + ``pygments``
     - Completed
   * - PDF (``.pdf``)
     - HTML (``.html``)
     - ``src/aichemist_transmutation_codex/converters/pdf_to_html.py``
     - ``PyMuPDF`` / ``pdfminer.six``
     - Completed
   * - PDF (``.pdf``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/pdf_to_markdown.py``
     - ``PyMuPDF`` + ``pytesseract``
     - Completed
   * - Scanned PDF (``.pdf``)
     - Searchable PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/pdf_to_editable_pdf.py``
     - ``ocrmypdf`` (``Tesseract``)
     - Completed
   * - Markdown (``.md``)
     - DOCX (``.docx``)
     - ``src/aichemist_transmutation_codex/converters/markdown_to_docx.py``
     - ``pypandoc`` / ``python-docx``
     - Completed
   * - DOCX (``.docx``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/doc_to_pdf.py``
     - ``docx2pdf`` / ``pandoc``
     - Completed
   * - HTML (``.html``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/html_to_markdown.py``
     - ``markdownify`` / ``html2text``
     - Planned
   * - DOCX (``.docx``)
     - HTML (``.html``)
     - ``src/aichemist_transmutation_codex/converters/doc_to_html.py``
     - ``python-docx`` / ``pypandoc``
     - Planned
   * - PDF (``.pdf``)
     - DOCX (``.docx``)
     - ``src/aichemist_transmutation_codex/converters/pdf_to_docx.py``
     - ``pdf2docx``
     - Planned
   * - HTML (``.html``)
     - DOCX (``.docx``)
     - ``src/aichemist_transmutation_codex/converters/html_to_docx.py``
     - ``pypandoc`` / ``html-docx-js`` (Node)
     - Planned
   * - Markdown (``.md``)
     - EPUB (``.epub``)
     - ``src/aichemist_transmutation_codex/converters/markdown_to_epub.py``
     - ``pypandoc`` / ``ebooklib``
     - Idea
   * - PDF (``.pdf``)
     - EPUB (``.epub``)
     - ``src/aichemist_transmutation_codex/converters/pdf_to_epub.py``
     - ``PyMuPDF`` + ``ebooklib`` (alt: Calibre CLI)
     - Idea
   * - TXT (``.txt``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/txt_to_markdown.py``
     - Python I/O, ``markdown`` (for parsing)
     - Idea
   * - Markdown (``.md``)
     - TXT (``.txt``)
     - ``src/aichemist_transmutation_codex/converters/markdown_to_txt.py``
     - ``markdown`` + ``html2text`` / ``BeautifulSoup``
     - Idea
   * - TXT (``.txt``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/txt_to_pdf.py``
     - ``reportlab`` / (TXT->MD->PDF chain)
     - Idea
   * - ODT (``.odt``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/odt_to_markdown.py``
     - ``odtpy`` / ``pypandoc``
     - Idea
   * - ODT (``.odt``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/odt_to_pdf.py``
     - ``pypandoc`` / (ODT->HTML->PDF chain)
     - Idea
   * - Markdown (``.md``)
     - ODT (``.odt``)
     - ``src/aichemist_transmutation_codex/converters/markdown_to_odt.py``
     - ``odtpy`` / ``pypandoc``
     - Idea
   * - XLSX (``.xlsx``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/xlsx_to_markdown.py``
     - ``openpyxl`` / ``pandas``
     - Idea
   * - XLSX (``.xlsx``)
     - CSV (``.csv``)
     - ``src/aichemist_transmutation_codex/converters/xlsx_to_csv.py``
     - ``openpyxl`` / ``pandas`` + ``csv`` module
     - Idea
   * - CSV (``.csv``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/csv_to_markdown.py``
     - ``csv`` module
     - Idea
   * - PPTX (``.pptx``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/pptx_to_pdf.py``
     - ``python-pptx`` + ``reportlab`` / ``pypandoc``
     - Idea
   * - PPTX (``.pptx``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/pptx_to_markdown.py``
     - ``python-pptx``
     - Idea
   * - IPYNB (``.ipynb``)
     - Markdown (``.md``)
     - ``src/aichemist_transmutation_codex/converters/ipynb_to_markdown.py``
     - ``nbconvert``
     - Idea
   * - IPYNB (``.ipynb``)
     - HTML (``.html``)
     - ``src/aichemist_transmutation_codex/converters/ipynb_to_html.py``
     - ``nbconvert``
     - Idea
   * - IPYNB (``.ipynb``)
     - PDF (``.pdf``)
     - ``src/aichemist_transmutation_codex/converters/ipynb_to_pdf.py``
     - ``nbconvert``
     - Idea

Conclusion
----------

These design decisions aim to create a maintainable, extendable, and user-friendly package. As the project evolves, we'll revisit these decisions to ensure they continue to serve the project's goals.

By documenting our decisions and their rationales, we provide context for future contributors and ensure consistency in the project's development.