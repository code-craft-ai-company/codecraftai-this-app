==========================
Automation Mojo This App
==========================

The ``automojo-this-app`` package is a foundational Python library that manages application presence and configuration for the Automation Mojo framework. It provides a lightweight configuration management system that allows applications to establish their presence on a user's machine with customizable settings. The package serves as the foundational configuration layer for Automation Mojo applications and tools, handling application identity, configuration-file discovery, environment-variable precedence, extensible module loading, and machine-specific presence establishment.

Highlights
==========

- Application identity and naming primitives.
- Configuration-file discovery and loading with well-defined precedence rules.
- Environment variable management for application presence variables.
- Extensible module loading for add-in components.
- Machine-specific presence establishment.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/`` - Package source code.
- ``source/tests/`` - ``unittest``-based tests.
- ``specs/`` - Requirements, design, and task documentation.
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-envrionment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run ``unittest`` tests:

.. code-block:: bash

   python -m unittest discover -s source/tests -p "test_*.py"

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
- Specifications: ``specs/thisapp/``
