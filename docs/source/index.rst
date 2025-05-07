Welcome to MDtoPDF's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   architecture/project_structure
   architecture/design_decisions
   usage/quickstart
   usage/installation
   usage/gui
   usage/batch_conversion
   usage/examples
   usage/mdx_conversion
   development/contributing
   development/autodoc_guide
   development/testing
   development/editable_pdf_research
   api/modules

MDtoPDF - Markdown to PDF Converter
----------------------------------

MDtoPDF is a versatile Python package for converting Markdown files to various formats, including PDF and HTML.
The package is designed to be extensible, allowing for easy addition of new output formats while maintaining a clean, consistent API.

Features
--------

* Convert Markdown files to PDF
* Convert Markdown files to HTML
* Convert PDF files to Markdown
* Command-line interface for easy usage
* Graphical user interface for intuitive file conversion
* Programmatic API for integration with other Python applications
* Extensible architecture for adding new output formats

Quick Start
----------

Installation
~~~~~~~~~~~

.. code-block:: bash

   # Basic installation
   pip install mdtopdf

   # Installation with GUI support
   pip install "mdtopdf[gui]"

Basic Usage - Command Line
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert a markdown file to PDF
   mdtopdf convert example.md --format pdf

   # Convert a markdown file to HTML
   mdtopdf convert example.md --format html

   # Use the GUI to select files
   mdtopdf-gui

Basic Usage - Python API
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from mdtopdf.converters import convert_md_to_pdf, convert_md_to_html
   from pathlib import Path

   # Convert to PDF
   pdf_path = convert_md_to_pdf('example.md')
   print(f"PDF saved to: {pdf_path}")

   # Convert to HTML
   html_path = convert_md_to_html('example.md')
   print(f"HTML saved to: {html_path}")

Documentation Overview
--------------------

This documentation is organized into several sections:

* **Architecture** - Information about the project structure and design decisions
* **Usage** - How to install and use the package, including GUI and command-line interfaces
* **Development** - Guidelines for contributing to the project, including documentation standards
* **API Reference** - Automatically generated documentation from code docstrings

The documentation is built using Sphinx with the autodoc extension, which automatically generates API documentation from docstrings in the code.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`