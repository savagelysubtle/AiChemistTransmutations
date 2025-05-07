# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
# Add the project root directory to the path so Sphinx can find the Python modules
sys.path.insert(0, os.path.abspath('..'))
# If using a src layout, uncomment this line:
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MDtoPDF'
copyright = '2025, MDtoPDF Team'
author = 'MDtoPDF Team'

version = '0.1.0'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',       # Core extension for API documentation
    'sphinx.ext.napoleon',      # Support for Google-style docstrings
    'sphinx.ext.viewcode',      # Add links to view source code
    'sphinx.ext.intersphinx',   # Link to other projects' documentation
    'sphinx.ext.todo',          # Support for TODO items
    'sphinx.ext.coverage',      # Check documentation coverage
    'sphinx.ext.autosummary',   # Generate summary tables for modules
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Autodoc configuration --------------------------------------------------
# Autodoc settings
autodoc_member_order = 'bysource'  # Document members in source code order
autodoc_typehints = 'description'  # Put type hints in the description instead of the signature
autodoc_class_signature = 'mixed'  # Show init parameters in class signature
autodoc_docstring_signature = True  # Try to extract signatures from docstrings
autoclass_content = 'both'  # Include both class and __init__ docstrings

# -- Napoleon configuration -------------------------------------------------
# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
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

# -- Intersphinx configuration ----------------------------------------------
# Intersphinx maps for linking to external documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}

# -- Todo configuration -----------------------------------------------------
# Todo settings
todo_include_todos = True  # Include TODOs in the documentation

# -- Additional configuration -----------------------------------------------
# Add any additional settings here
