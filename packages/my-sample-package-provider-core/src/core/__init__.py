"""
core package - shared utilities and base logic for the monorepo.
"""

from core.models import DataModel
from core.utils import format_message, process_data

__all__ = ["DataModel", "format_message", "process_data"]

try:
    from core._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"
