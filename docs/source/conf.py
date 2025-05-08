# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the project root directory to the path so Sphinx can find the Python modules
sys.path.insert(0, os.path.abspath("../.."))  # Adjusted path for docs/source
# If using a src layout, uncomment this line:
sys.path.insert(0, os.path.abspath("../../src"))  # Adjusted path for docs/source

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Aichemist Transmutation Codex"
copyright = "2025, Aichemist Transmutation Codex Team"
author = "Aichemist Transmutation Codex Team"

version = "0.1.0"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Core Sphinx extensions
    "sphinx.ext.autodoc",  # AutomaticallyW document from docstrings
    "sphinx.ext.autosummary",  # Generate summary tables for modules/classes
    # Type hint handling - place after autodoc, often before napoleon
    "sphinx_autodoc_typehints",  # Improved type hint rendering (ensure this package is installed)
    # Docstring parsing
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    # Linking and navigation
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.intersphinx",  # Link to other projects' documentation (e.g., Python, Sphinx)
    "sphinx.ext.autosectionlabel",  # Allow referencing sections using their titles
    # Utility and specific features
    "sphinx.ext.todo",  # Support for TODO items and directives
    "sphinx.ext.coverage",  # Check documentation coverage
    "sphinx.ext.inheritance_diagram",  # Generate inheritance diagrams for classes
    # UI Enhancements
    "sphinx_copybutton",  # Add a "copy" button to code blocks (ensure this package is installed)
    "sphinx_design",  # For creating beautiful, responsive web components (ensure this package is installed)
]

templates_path = ["_templates"]  # Relative to source directory
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]  # Relative to source directory (docs/source/_static)

# html_css_files: A list of CSS files. The entry must be a filename string or a
# tuple containing the filename string and the attributes dictionary.
# The filename must be relative to the html_static_path, or a full URI with
# scheme like http://example.org/style.css.
html_css_files = [
    "custom.css",  # Our custom CSS for the dark theme and lime green accents
]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# You will need to create this file in docs/source/_static/logo.png
html_logo = "_static/logo.png"

# The name of an image file (relative to this directory) to use as a favicon of
# the docs. This should be a Windows icon file (.ico) or a PNG/GIF file.
# You will need to create this file in docs/source/_static/favicon.ico or .png
html_favicon = "_static/favicon.ico"

# -- Pygments (syntax highlighting) style ------------------------------------
# The name of the Pygments (syntax highlighting) style to use.
# 'monokai' is a popular dark theme. Others include 'native', 'dracula', 'fruity'.
pygments_style = "monokai"

# -- Autodoc configuration --------------------------------------------------
# Autodoc settings
autodoc_member_order = "bysource"  # Document members in source code order
autodoc_typehints = (
    "description"  # Put type hints in the description instead of the signature.
    # sphinx_autodoc_typehints will use this setting.
)
autodoc_class_signature = "mixed"  # Show __init__ parameters in class signature
autodoc_docstring_signature = True  # Try to extract signatures from docstrings
autoclass_content = "both"  # Include both class and __init__ docstrings

# -- sphinx-autodoc-typehints configuration ---------------------------------
# (sphinx_autodoc_typehints uses the autodoc_typehints setting above)
# For more granular control with sphinx_autodoc_typehints, you can set:
# always_document_param_types = True  # If True, always include type hints for parameters
# typehints_fully_qualified = False   # If True, show full package paths for types
# typehints_document_rtype = True     # If True, document the return type hint

# -- Napoleon configuration -------------------------------------------------
# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True  # Keep True if you might mix styles, else False
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
napoleon_preprocess_types = False  # Set to True if you want napoleon to process types before sphinx_autodoc_typehints
napoleon_attr_annotations = True

# -- Intersphinx configuration ----------------------------------------------
# Intersphinx maps for linking to external documentation
# Example: :py:class:`zipfile.ZipFile` will link to the Python documentation.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    # You can add mappings to other libraries your project uses, e.g.:
    # "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- Todo configuration -----------------------------------------------------\r
# Todo settings
todo_include_todos = True  # If True, .. todo:: directives will be shown in the output

# -- Autosectionlabel configuration -----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html
# This allows you to create references like :ref:`My Section Title`
autosectionlabel_prefix_document = (
    True  # Prepends document path to label to ensure uniqueness.
)
# E.g., 'usage/quickstart:Introduction'

# -- Inheritance Diagram configuration --------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/inheritance.html
# This extension can generate graphical inheritance diagrams.
# Requires graphviz to be installed on the system.
# inheritance_graph_attrs = dict(rankdir="LR", size='"6.0, 8.0"', fontsize=14, ratio='compress')
# graphviz_output_format = "svg" # "png" or "svg"

# -- Copybutton configuration -----------------------------------------------
# https://sphinx-copybutton.readthedocs.io/en/latest/configuration.html
# This adds a small copy button to the top right of your code blocks.
# You can customize it, for example, to strip command line prompts:
# copybutton_prompt_text = r">>> |\.\.\. |\$ |In \\[[0-9]+\\]: " # Regex for prompts
# copybutton_prompt_is_regexp = True
# copybutton_only_copy_prompt_lines = True # Only copy lines with prompts (e.g. for shell sessions)

# -- Additional configuration -----------------------------------------------
# Add any additional settings here
# Example: Add a logo
# html_logo = "_static/logo.png"

# Example: Custom CSS (place custom.css in _static folder)
# html_css_files = [
# 'custom.css',
# ]
