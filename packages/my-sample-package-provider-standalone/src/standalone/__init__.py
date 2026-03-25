"""standalone package - independent utilities with no monorepo dependencies."""

from standalone.math import clamp, lerp
from standalone.text import slugify, truncate

__all__ = ["clamp", "lerp", "slugify", "truncate"]

try:
    from standalone._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"
