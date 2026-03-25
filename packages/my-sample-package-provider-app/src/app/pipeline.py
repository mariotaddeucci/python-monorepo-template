"""Pipeline module for the app package.

When the `core` optional dependency is installed, the pipeline is able
to deserialize raw records into typed DataModel instances using
core.utils.process_data. Otherwise it works with plain dicts.
"""

from __future__ import annotations

from typing import Any

try:
    from core.utils import filter_by_tag, process_data

    _CORE_AVAILABLE = True
except ImportError:
    _CORE_AVAILABLE = False


class Pipeline:
    """A simple data processing pipeline.

    When `core` is installed the pipeline can load records as typed
    DataModel objects. Without it, records are kept as raw dicts.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._records: list[Any] = []

    @property
    def has_core(self) -> bool:
        """Return True if the `core` package is available."""
        return _CORE_AVAILABLE

    def load(self, records: list[dict]) -> Pipeline:
        """Load raw records into the pipeline.

        If `core` is installed, records are converted to DataModel instances.
        Otherwise they are stored as plain dicts.

        Args:
            records: List of raw record dictionaries.

        Returns:
            self, for method chaining.
        """
        if _CORE_AVAILABLE:
            self._records = process_data(records)
        else:
            self._records = list(records)
        return self

    def filter_tag(self, tag: str) -> Pipeline:
        """Filter records by tag (requires `core` extra).

        Args:
            tag: The tag to filter by.

        Returns:
            self, for method chaining.

        Raises:
            RuntimeError: If `core` is not installed.
        """
        if not _CORE_AVAILABLE:
            raise RuntimeError("Tag filtering requires the 'core' extra: pip install app[core]")
        self._records = filter_by_tag(self._records, tag)
        return self

    def results(self) -> list[Any]:
        """Return the current records in the pipeline."""
        return list(self._records)

    def count(self) -> int:
        """Return the number of records currently in the pipeline."""
        return len(self._records)
