\
Using Autodoc for API Documentation
================================

This guide explains how to use Sphinx\'s autodoc extension to automatically generate API documentation from docstrings in your code.

Introduction to Autodoc
----------------------

Sphinx\'s autodoc extension allows you to include documentation from docstrings in your generated documentation. This means you can write your API documentation directly in your code and have it automatically extracted and formatted by Sphinx.

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
          \'sphinx.ext.autodoc\',
          \'sphinx.ext.viewcode\',
          \'sphinx.ext.napoleon\',  # For Google/NumPy style docstrings
          # other extensions...
      ]

2. Configure autodoc settings:

   .. code-block:: python

      # Autodoc settings
      autodoc_member_order = \'bysource\'  # or \'alphabetical\' or \'groupwise\'
      autodoc_typehints = \'description\'  # or \'signature\' or \'none\'
      autodoc_class_signature = \'mixed\'  # or \'separated\'
      autodoc_docstring_signature = True
      autoclass_content = \'both\'  # Include both class and __init__ docstrings

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

   .. automodule:: aichemist_transmutation_codex.converters.some_converter
      :members:
      :undoc-members:
      :show-inheritance:

   .. autoclass:: aichemist_transmutation_codex.SomeClass
      :members:
      :undoc-members:
      :special-members: __init__
      :show-inheritance:

   .. autofunction:: aichemist_transmutation_codex.converters.some_function

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

   sphinx-apidoc -o docs/source/api src/aichemist_transmutation_codex

This creates an RST file for each module in your package. You\'ll need to include these files in your documentation\'s toctree:

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

   \"\"\"Converter module for Aichemist Transmutation Codex.

   This module provides functionality to convert files between various formats
   using different engines.
   \"\"\"

Function Docstrings
~~~~~~~~~~~~~~~~~

Functions should have comprehensive docstrings:

.. code-block:: python

   def convert_file_format(input_path: str | Path, output_path: str | Path = None) -> Path:
       \"\"\"Convert a file from one format to another.

       Converts the given file using the appropriate registered converter.

       Args:
           input_path: Path to the file to convert.
           output_path: Path where the converted file should be saved.
               If not provided, the converted file will be saved in the same directory
               as the input file with an appropriate extension.

       Returns:
           Path object pointing to the generated converted file.

       Raises:
           FileNotFoundError: If the input file does not exist.
           PermissionError: If there are permission issues with the output location.
           ConversionError: If the conversion fails for any reason.

       Examples:
           >>> converted_path = convert_file_format(\"mydoc.md\", \"output.pdf\")
           >>> converted_path.name
           \'output.pdf\'
       \"\"\"

Class Docstrings
~~~~~~~~~~~~~~

Classes should have docstrings for both the class and its methods:

.. code-block:: python

   class BaseConverter:
       \"\"\"Handles conversion between specific formats.

       This class provides a base for specific converter implementations
       detailing supported formats and conversion logic.

       Attributes:
           engine: The conversion engine to use (if applicable).
           options: Dictionary of options for the converter.
       \"\"\"

       def __init__(self, engine: str = \"default\", options: dict = None):
           \"\"\"Initialize a BaseConverter.

           Args:
               engine: Name of the conversion engine to use.
               options: Dictionary of converter-specific options.
           \"\"\"
           self.engine = engine
           self.options = options or {}

       def convert(self, input_path: str | Path, output_path: str | Path = None) -> Path:
           \"\"\"Convert a file.

           Args:
               input_path: Path to the input file.
               output_path: Path where to save the converted file.

           Returns:
               Path to the generated file.
           \"\"\"

Advanced Autodoc Features
-----------------------

Selective Documentation
~~~~~~~~~~~~~~~~~~~~~

You can be selective about what gets documented:

.. code-block:: rst

   .. automodule:: aichemist_transmutation_codex.converters
      :members: convert_pdf_to_md, convert_md_to_html
      :undoc-members:
      :noindex:

Cross-referencing
~~~~~~~~~~~~~~~

You can cross-reference other documented objects:

.. code-block:: rst

   You can use :func:`aichemist_transmutation_codex.converters.convert_file_format` to convert files.

   See :class:`aichemist_transmutation_codex.BaseConverter` for more advanced conversion options.

In docstrings:

.. code-block:: python

   def some_function():
       \"\"\"This function does something.

       See Also:
           :func:`other_function`: For related functionality.
       \"\"\"

Including Private Members
~~~~~~~~~~~~~~~~~~~~~~~

By default, autodoc doesn\'t document private members (those starting with an underscore):

.. code-block:: rst

   .. automodule:: my_module
      :members:
      :private-members: _my_private_function

Excluding Members
~~~~~~~~~~~~~~~~~

You can exclude specific members:

.. code-block:: rst

   .. automodule:: my_module
      :members:
      :exclude-members: secret_function, AnotherClass.secret_method

Using autodoc_default_options
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can set default options for all autodoc directives in ``conf.py``:

.. code-block:: python

   autodoc_default_options = {
       \'members\': True,
       \'member-order\': \'bysource\',
       \'special-members\': \'__init__\',
       \'undoc-members\': True,
       \'exclude-members\': \'__weakref__\'
   }

This can reduce repetition in your RST files.

Tips for Good API Documentation
-------------------------------

- **Be comprehensive**: Document all public modules, classes, functions, and methods.
- **Be clear and concise**: Use simple language and avoid jargon where possible.
- **Provide examples**: Code examples make it much easier for users to understand how to use your API.
- **Document parameters and return values**: Clearly explain what each parameter does and what the function returns.
- **Document exceptions**: List any exceptions that your code might raise.
- **Keep it up-to-date**: Ensure your documentation reflects the current state of your code.
- **Use cross-references**: Link to related parts of your API or documentation.

Troubleshooting Autodoc
-----------------------

- **Module not found**: Ensure your project\'s source directory is in ``sys.path`` in your ``conf.py``.
- **Docstrings not appearing**: Check that your docstrings are correctly formatted and that the autodoc directives are correct.
- **Incorrect formatting**: Verify your Napoleon settings if you are using Google or NumPy style docstrings.

Further Reading
---------------

- `Sphinx Autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_
- `Sphinx Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_
- `Google Style Python Docstrings <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_