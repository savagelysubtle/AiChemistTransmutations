\
Installation
============

This section guides you through installing the Aichemist Transmutation Codex and its dependencies.

Prerequisites
-------------

Before you begin, ensure you have the following installed on your system:

*   **Python**: Version 3.13 or higher. You can download Python from `python.org <https://www.python.org/>`_.
*   **UV (Python Package Installer)**: This project uses `UV <https://github.com/astral-sh/uv>`_ for managing Python dependencies and virtual environments. If you don't have it, you can install it via pip or other methods described in its documentation.

    .. code-block:: console

       pip install uv

*   **Git**: For cloning the repository (if installing from source).
*   **(Optional for GUI)** **Node.js and npm/yarn**: If you plan to develop or run the GUI, you'll need Node.js (which includes npm). You can download it from `nodejs.org <https://nodejs.org/>`_.
*   **(Optional for some converters)** Specific system libraries or applications may be required by certain converters (e.g., Tesseract OCR for PDF to MD with OCR, or wkhtmltopdf for some HTML to PDF conversions). These will be noted in the specific converter's documentation if applicable.

Installation Methods
--------------------

Choose one of the following methods to install the Aichemist Transmutation Codex.

Method 1: Installing from PyPI (Recommended for Users)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the recommended method for most users who want to use the application or library.

.. code-block:: console

   uv pip install aichemist-transmutation-codex

This will install the latest stable release from the Python Package Index (PyPI).

Method 2: Installing from Source (Recommended for Developers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to contribute to the project, or need the very latest changes, you can install from source.

1.  **Clone the repository**:

    .. code-block:: console

       git clone https://github.com/your-username/AichemistTransmutationCodex.git
       cd AichemistTransmutationCodex

2.  **Create and activate a virtual environment using UV**:

    .. code-block:: console

       uv venv
       source .venv/bin/activate  # On Linux/macOS
       # .\.venv\Scripts\activate   # On Windows (Command Prompt)
       # .\.venv\Scripts\Activate.ps1 # On Windows (PowerShell)

3.  **Install the project and its dependencies**:

    This will install the package in editable mode, meaning changes you make to the source code will be immediately reflected when you run the application.

    .. code-block:: console

       uv pip install -e ".[dev,gui]"

    *   The `[dev]` extra includes dependencies needed for development (e.g., linters, test runners).
    *   The `[gui]` extra includes dependencies needed for the GUI (if you plan to use or develop it).
    *   You can omit `[gui]` if you only intend to use the CLI or library components.

Setting up the GUI (If Installed from Source)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you installed from source and included the `[gui]` extra, you also need to install the Node.js dependencies for the Electron GUI:

1.  **Navigate to the GUI directory**:

    .. code-block:: console

       cd gui

2.  **Install Node.js dependencies**:

    .. code-block:: console

       npm install
       # or if you prefer yarn:
       # yarn install

Verifying the Installation
--------------------------

After installation, you should be able to run the command-line interface:

.. code-block:: console

   transmute --help

This should display the help message for the Aichemist Transmutation Codex CLI.

If you installed the GUI, you can try running it (from the project root directory):

.. code-block:: console

   npm run gui-dev # (or the appropriate script from your package.json)
   # or directly via the run-gui.bat script if configured

Troubleshooting
---------------

*   **Command not found (`transmute` or `uv`)**: Ensure that the directory containing the executables (Python's scripts directory or UV's installation directory) is in your system's PATH environment variable.
*   **Missing dependencies**: If a specific converter fails due to a missing external dependency (like Tesseract), please refer to that converter's documentation or error message for installation instructions for that dependency.

Next Steps
----------

Once installed, you can proceed to the :doc:`usage` section to learn how to use the Aichemist Transmutation Codex.