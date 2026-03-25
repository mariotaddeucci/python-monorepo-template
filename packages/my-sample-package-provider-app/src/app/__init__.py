"""
app package - application layer for the monorepo.

The `core` extra is optional. When installed, richer processing
via core.DataModel becomes available through the pipeline module.
"""

from app.pipeline import Pipeline
from app.reporter import Reporter

__all__ = ["Pipeline", "Reporter"]

try:
    from app._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"
