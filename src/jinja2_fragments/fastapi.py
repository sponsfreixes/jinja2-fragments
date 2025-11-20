"""FastAPI integration for jinja2-fragments.

This module provides FastAPI-compatible template rendering with support for
rendering individual Jinja2 blocks. It's built on top of the Starlette
implementation since FastAPI uses Starlette under the hood.

For pure Starlette applications, you can use jinja2_fragments.starlette directly.
"""

from __future__ import annotations

try:
    # Verify that Starlette is available (FastAPI requires it)
    import starlette  # noqa: F401
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Install FastAPI (which includes Starlette) to use jinja2_fragments.fastapi"
    ) from e

# Import everything from the starlette module to maintain backward compatibility
from .starlette import InvalidContextError, Jinja2Blocks

# Re-export for backward compatibility
__all__ = ["InvalidContextError", "Jinja2Blocks"]
