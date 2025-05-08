\
Development Guide
=================

This section provides information and guidelines for developers working on or contributing to the Aichemist Transmutation Codex.

.. toctree::
   :maxdepth: 2
   :caption: Development Topics:

   editable_pdf_research
   # Add other development-specific guides here, e.g.:
   # coding_style
   # testing_guidelines
   # release_process

Key Development Aspects:
------------------------

*   **API Documentation (Autodocs)**: The API reference documentation is automatically generated from docstrings in the Python source code (`src/aichemist_transmutation_codex`).
    *   This process is handled by the `docs/generate_api_docs.py` script (using `sphinx-apidoc`) and `sphinx.ext.autodoc`.
    *   The generated API docs are included in the main table of contents under :doc:`../api/modules`.
    *   Ensure all new code (modules, classes, functions, methods) has clear, comprehensive Google-style docstrings.

*   **Setting up the Development Environment**: Refer to the :doc:`../installation` guide for instructions on installing from source and setting up the development environment with UV.

*   **Running Tests**: (Assuming pytest is used, as per design_decisions.rst)
    To run the test suite, navigate to the project root directory and execute:

    .. code-block:: console

       pytest

    Or, if using UV scripts defined in `pyproject.toml`:

    .. code-block:: console

       uv run test

*   **Coding Style & Linting**: We use Ruff for linting and formatting. Before committing, please run:

    .. code-block:: console

       ruff check . --fix
       ruff format .

*   **Contribution Workflow**: See the :doc:`../contributing` guide for details on how to contribute changes.

*   **Project Rules & Guidelines**: Always refer to the established project rules for consistency:
    *   :cursor_rule:`001-global-project-context`
    *   :cursor_rule:`800-feature-development`
    *   :cursor_rule:`811-electron-main-preload-guidelines` (for GUI development)
