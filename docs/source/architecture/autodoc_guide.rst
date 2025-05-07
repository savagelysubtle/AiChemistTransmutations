Using Autodoc for API Documentation
================================

This guide explains how to use Sphinx's autodoc extension to automatically generate API documentation from docstrings in your code.

Introduction to Autodoc
----------------------

Sphinx's autodoc extension allows you to include documentation from docstrings in your generated documentation. This means you can write your API documentation directly in your code and have it automatically extracted and formatted by Sphinx.

Benefits of Autodoc:

- Keep documentation close to the code
- Reduce duplication between code comments and external documentation
- Documentation stays up-to-date as the code changes
- Consistent formatting and structure

Setting Up Autodoc
-----------------

1. Ensure autodoc is enabled in your ``conf.py``:

   .. code-block:: python

      extensions = [
          'sphinx.ext.autodoc',
          'sphinx.ext.viewcode',
          'sphinx.ext.napoleon',  # For Google/NumPy style docstrings
          # other extensions...
      ]

2. Configure autodoc settings:

   .. code-block:: python

      # Autodoc settings
      autodoc_member_order = 'bysource'  # or 'alphabetical' or 'groupwise'
      autodoc_typehints = 'description'  # or 'signature' or 'none'
      autodoc_class_signature = 'mixed'  # or 'separated'
      autodoc_docstring_signature = True
      autoclass_content = 'both'  # Include both class and __init__ docstrings

3. Set up Napoleon extension for Google-style docstrings:

   .. code-block:: python

      # Napoleon settings for Google-style docstrings
      napoleon_google_docstring = True
      napoleon_numpy_docstring = True
      napoleon_include_init_with_doc = False
      napoleon_include_private_with_doc = False
      napoleon_include_special_with_doc = True
      napoleon_use_admonition_for_examples = True
      napoleon_use_admonition_for_notes = True
      napoleon_use_admonition_for_references = True
      napoleon_use_ivar = False
      napoleon_use_param = True
      napoleon_use_rtype = True
      napoleon_use_keyword = True
      napoleon_preprocess_types = False
      napoleon_attr_annotations = True

Generating API Documentation
--------------------------

There are two main approaches to using autodoc:

1. **Manual directives**: Write RST files with autodoc directives
2. **sphinx-apidoc**: Generate RST files automatically from your Python modules

Using Manual Directives
~~~~~~~~~~~~~~~~~~~~~~

You can use autodoc directives directly in your RST files:

.. code-block:: rst

   .. automodule:: mdtopdf.converters.markdown_to_pdf
      :members:
      :undoc-members:
      :show-inheritance:

   .. autoclass:: mdtopdf.SomeClass
      :members:
      :undoc-members:
      :special-members: __init__
      :show-inheritance:

   .. autofunction:: mdtopdf.converters.convert_md_to_pdf

Common Autodoc Directives:

* ``.. automodule::`` - Document a module
* ``.. autoclass::`` - Document a class
* ``.. autofunction::`` - Document a function
* ``.. automethod::`` - Document a method
* ``.. autoattribute::`` - Document an attribute
* ``.. autoexception::`` - Document an exception

Using sphinx-apidoc
~~~~~~~~~~~~~~~~~~

sphinx-apidoc automatically generates RST files with autodoc directives:

.. code-block:: bash

   sphinx-apidoc -o docs/source/api src/mdtopdf

This creates an RST file for each module in your package. You'll need to include these files in your documentation's toctree:

.. code-block:: rst

   .. toctree::
      :maxdepth: 2
      :caption: API Reference:

      api/modules

Writing Docstrings for Autodoc
----------------------------

For autodoc to work effectively, your code needs well-written docstrings. We use Google-style docstrings for our project.

Module Docstrings
~~~~~~~~~~~~~~~~

Every module should have a docstring at the beginning:

.. code-block:: python

   """PDF converter module for MDtoPDF.

   This module provides functionality to convert Markdown files to PDF format
   using various PDF rendering engines.
   """

Function Docstrings
~~~~~~~~~~~~~~~~~

Functions should have comprehensive docstrings:

.. code-block:: python

   def convert_md_to_pdf(input_path: str | Path, output_path: str | Path = None) -> Path:
       """Convert a Markdown file to PDF.

       Converts the given Markdown file to PDF format using the default PDF renderer.

       Args:
           input_path: Path to the Markdown file to convert
           output_path: Path where the PDF file should be saved.
               If not provided, the PDF will be saved in the same directory
               as the input file.

       Returns:
           Path object pointing to the generated PDF file.

       Raises:
           FileNotFoundError: If the input file does not exist
           PermissionError: If there are permission issues with the output location
           ConversionError: If the conversion fails for any reason

       Examples:
           >>> pdf_path = convert_md_to_pdf("example.md")
           >>> pdf_path.name
           'example.pdf'
       """

Class Docstrings
~~~~~~~~~~~~~~

Classes should have docstrings for both the class and its methods:

.. code-block:: python

   class PDFConverter:
       """Handles conversion of Markdown to PDF.

       This class provides methods for converting Markdown documents to PDF
       using different rendering engines and options.

       Attributes:
           renderer: The PDF rendering engine to use
           options: Dictionary of options for the renderer
       """

       def __init__(self, renderer: str = "default", options: dict = None):
           """Initialize a PDFConverter.

           Args:
               renderer: Name of the rendering engine to use
               options: Dictionary of renderer-specific options
           """
           self.renderer = renderer
           self.options = options or {}

       def convert(self, input_path: str | Path, output_path: str | Path = None) -> Path:
           """Convert a Markdown file to PDF.

           Args:
               input_path: Path to the Markdown file
               output_path: Path where to save the PDF

           Returns:
               Path to the generated PDF
           """

Advanced Autodoc Features
-----------------------

Selective Documentation
~~~~~~~~~~~~~~~~~~~~~

You can be selective about what gets documented:

.. code-block:: rst

   .. automodule:: mdtopdf.converters
      :members: convert_md_to_pdf, convert_md_to_html
      :undoc-members:
      :noindex:

Cross-referencing
~~~~~~~~~~~~~~~

You can cross-reference other documented objects:

.. code-block:: rst

   You can use :func:`mdtopdf.converters.convert_md_to_pdf` to convert Markdown to PDF.

   See :class:`mdtopdf.PDFConverter` for more advanced conversion options.

In docstrings:

.. code-block:: python

   def some_function():
       """This function does something.

       See Also:
           :func:`other_function`: For related functionality
       """

Including Private Members
~~~~~~~~~~~~~~~~~~~~~~~

By default, autodoc doesn't document private members (those starting with an underscore):

.. code-block:: rst

   .. automodule:: mdtopdf.converters
      :members:
      :private-members:  # Include private members
      :special-members: __init__, __str__  # Include specific special members

Documentation Tips
----------------

1. **Be consistent**: Follow the same docstring style throughout your code
2. **Be complete**: Document all parameters, return values, and exceptions
3. **Include examples**: Practical examples help users understand how to use your code
4. **Update docstrings**: Keep docstrings up-to-date when you change code
5. **Test your documentation**: Make sure autodoc generates what you expect

Building and Checking Documentation
---------------------------------

After writing docstrings, build your documentation to see the results:

.. code-block:: bash

   sphinx-build -b html docs/source docs/build/html

Check for warning messages during the build process. These often indicate issues with your docstrings or autodoc directives.

Automated API Documentation Workflow
----------------------------------

For large projects, consider automating the API documentation process:

1. Run ``sphinx-apidoc`` as part of your documentation build process
2. Set up documentation checks in your CI pipeline
3. Configure auto-commits or notifications for documentation changes

Conclusion
---------

Using autodoc with Sphinx provides a powerful way to maintain accurate, up-to-date API documentation directly from your code. By following the guidelines in this document, you'll be able to create comprehensive documentation that stays in sync with your code.