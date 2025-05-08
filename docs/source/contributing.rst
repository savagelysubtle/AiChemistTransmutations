\
Contributing
============

Thank you for your interest in contributing to the Aichemist Transmutation Codex! We welcome contributions of all kinds, from bug reports and feature requests to code contributions and documentation improvements.

Ways to Contribute
------------------

*   **Reporting Bugs**: If you find a bug, please open an issue on our `GitHub Issues <https://github.com/your-username/AichemistTransmutationCodex/issues>`_ page. Provide as much detail as possible, including steps to reproduce the bug, expected behavior, and actual behavior.
*   **Suggesting Enhancements**: Have an idea for a new feature or an improvement to an existing one? Open an issue to discuss it.
*   **Writing Documentation**: Good documentation is crucial. If you find areas that are unclear or missing, please let us know or consider submitting a pull request with improvements.
*   **Submitting Code**: If you want to contribute code, please follow the development workflow outlined below.

Development Workflow
--------------------

1.  **Fork the Repository**: Start by forking the `AichemistTransmutationCodex repository <https://github.com/your-username/AichemistTransmutationCodex>`_ on GitHub.
2.  **Clone Your Fork**: Clone your forked repository to your local machine.

    .. code-block:: console

       git clone https://github.com/YOUR_USERNAME/AichemistTransmutationCodex.git
       cd AichemistTransmutationCodex

3.  **Set up your Development Environment**:
    *   Follow the :doc:`installation` guide for installing from source, including setting up UV and the virtual environment.
    *   Install development dependencies:

        .. code-block:: console

           uv pip install -e ".[dev,gui]"  # Include [gui] if working on the GUI

4.  **Create a New Branch**: Create a new branch for your feature or bugfix. Use a descriptive name.

    .. code-block:: console

       git checkout -b feature/your-awesome-feature
       # or
       # git checkout -b fix/issue-123-bug-description

5.  **Make Your Changes**: Write your code, add tests, and update documentation as needed.
    *   **Coding Style**: Please adhere to the project's coding style. We use Ruff for linting and formatting. Run `ruff check . --fix` and `ruff format .` before committing.
    *   **Type Hints**: Use Python type hints for all new code.
    *   **Docstrings**: Write clear and comprehensive docstrings for all modules, classes, and functions (Google Style preferred).
    *   **Tests**: Add unit tests for new functionality in the `tests/unit/` directory and integration tests in `tests/integration/` if applicable. Ensure all tests pass by running `pytest`.

6.  **Commit Your Changes**: Make clear, concise commit messages.

    .. code-block:: console

       git add .
       git commit -m "feat: Add awesome new feature X that does Y"
       # or
       # git commit -m "fix: Resolve issue #123 by fixing Z"

7.  **Push to Your Fork**: Push your changes to your forked repository.

    .. code-block:: console

       git push origin feature/your-awesome-feature

8.  **Submit a Pull Request (PR)**: Open a pull request from your branch on your fork to the `main` branch of the original AichemistTransmutationCodex repository.
    *   Provide a clear description of your changes in the PR.
    *   Link to any relevant issues.
    *   Ensure all CI checks pass.

Code of Conduct
---------------

While we don't have a formal Code of Conduct document yet, we expect all contributors to engage in a respectful and constructive manner. Please be considerate of others and foster a positive and inclusive community environment.

Questions?
----------

If you have any questions about contributing, feel free to open an issue or reach out to the maintainers.

Thank you for helping make the Aichemist Transmutation Codex better!