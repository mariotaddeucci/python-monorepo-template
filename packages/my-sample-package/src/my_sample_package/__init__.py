"""
my-sample-package — proxy package.

Lazily re-exports all symbols from installed providers:
  - my-sample-package-provider-core   → core.*
  - my-sample-package-provider-app    → app.*
  - my-sample-package-provider-standalone → standalone.*

Only providers that are actually installed are exposed; importing a symbol
from a missing provider raises ImportError with a helpful message.
"""

from __future__ import annotations

import importlib
import sys
from types import ModuleType

try:
    from my_sample_package._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

# Mapping: attribute name → (provider_module, install_extra)
_ATTR_MAP: dict[str, tuple[str, str]] = {}

_PROVIDERS: list[tuple[str, str]] = [
    ("core", "my-sample-package[core]"),
    ("app", "my-sample-package[app]"),
    ("standalone", "my-sample-package[standalone]"),
]

for _mod_name, _extra in _PROVIDERS:
    try:
        _mod: ModuleType = importlib.import_module(_mod_name)
        _all: list[str] = getattr(_mod, "__all__", [])
        for _name in _all:
            _ATTR_MAP[_name] = (_mod_name, _extra)
    except ImportError:
        pass


def __getattr__(name: str) -> object:
    if name in _ATTR_MAP:
        mod_name, extra = _ATTR_MAP[name]
        mod = sys.modules.get(mod_name) or importlib.import_module(mod_name)
        return getattr(mod, name)
    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}. "
        f"Install a provider extra to expose its symbols, e.g. `pip install {_suggest_extra(name)}`."
    )


def _suggest_extra(name: str) -> str:  # noqa: ARG001
    return "my-sample-package[all]"


def __dir__() -> list[str]:
    return [*list(_ATTR_MAP.keys()), "__version__", "__all__"]


__all__ = list(_ATTR_MAP.keys())
