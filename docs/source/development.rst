
Development
===========

This guide will help you set up your development environment for contributing to the ``jinja2-fragments`` project.

Development Environment Setup
=============================

Prerequisites
-------------

- Python 3.9 or higher
- pip
- git

Getting Started
---------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/sponsfreixes/jinja2-fragments
      cd jinja2-fragments

2. Create and activate a virtual environment:

   .. code-block:: bash

      # Using venv
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      
3. Install the package in development mode with all dependencies:

   .. code-block:: bash

      pip install -e ".[dev,tests,docs]"

4. Install pre-commit hooks:

   .. code-block:: bash

      pre-commit install

Running Tests
=============

We use ``pytest`` for testing. To run the tests:

.. code-block:: bash

   pytest

Pre-commit Hooks
================

We use ``pre-commit`` hooks to run `Ruff <https://docs.astral.sh/ruff/>`_ automatically before each commit. Make sure to install them before commiting.
The hooks are configured in the ``.pre-commit-config.yaml`` file.

Additionally, you can run the pre-commit hooks manually against all files:

.. code-block:: bash

   pre-commit run --all-files

Building Documentation
======================

We use `Sphinx <https://www.sphinx-doc.org/>`_ to build the documentation. The sources are on ``docs/source``.

To build the documentation locally:

.. code-block:: bash

   cd docs
   sphinx-build source/ build/  # Or using Make: make html

The built documentation will be available in the ``docs/build/html`` directory. Open ``index.html`` in your browser to view it.

Contribution Guidelines
=======================

Code Style
----------

We follow these coding conventions:

- **PEP 8**: For general Python style guidelines
- **Type annotations**: All new code should include proper type annotations
- **Docstrings**: Use Google-style docstrings for all functions, classes, and methods

Pull Request Process
--------------------

1. Create a new branch for your feature or bugfix.
2. Make your changes and ensure all tests pass. Add new tests if needed.
3. Run pre-commit hooks to ensure code quality (this should happen automatically on commit).
4. Update documentation if necessary.
5. Create a pull request with a clear description of the changes.
6. Link to any related issues.

For significant changes, consider first opening an issue to discuss the proposed changes.

Testing Requirements
--------------------

All new features should include tests. We aim to maintain high test coverage.

When fixing bugs, please add a test that reproduces the bug to ensure it doesn't return.

Framework Support
-----------------

``jinja2-fragments`` supports multiple web frameworks. If you're adding features that should work across frameworks:

1. Implement the core functionality in the base module
2. Add framework-specific integration for each supported framework
3. Add tests for each framework integration

Documentation
-------------

Update documentation for any new features or changes to existing functionality:

- Include docstrings for all public functions and classes
- Update the relevant sections in the documentation
- Add examples of how to use new features
- If applicable, explain differences between framework integrations

Getting Help
============

If you need help with the development process, you can:

- Open an issue on GitHub
- Reach out to project maintainers

Thank you for contributing to ``jinja2-fragments``!

