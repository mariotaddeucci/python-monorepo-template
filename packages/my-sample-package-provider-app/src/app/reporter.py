"""Reporter module for the app package.

Formats pipeline results into human-readable reports or structured output.
"""

from __future__ import annotations

from typing import Any


class Reporter:
    """Formats and presents pipeline results."""

    def __init__(self, title: str = "Report") -> None:
        self.title = title

    def summary(self, records: list[Any]) -> str:
        """Return a plain-text summary of the records.

        Args:
            records: List of records (DataModel or dict).

        Returns:
            A formatted summary string.
        """
        lines = [f"=== {self.title} ===", f"Total records: {len(records)}", ""]
        for i, record in enumerate(records, start=1):
            if hasattr(record, "to_dict"):
                data = record.to_dict()
            elif isinstance(record, dict):
                data = record
            else:
                data = {"value": str(record)}

            name = data.get("name", data.get("id", f"Record {i}"))
            value = data.get("value", "N/A")
            tags = data.get("tags", [])
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            lines.append(f"  {i}. {name}: {value}{tag_str}")

        return "\n".join(lines)

    def as_dicts(self, records: list[Any]) -> list[dict]:
        """Serialize records to a list of dictionaries.

        Args:
            records: List of records (DataModel or dict).

        Returns:
            A list of plain dictionaries.
        """
        result = []
        for record in records:
            if hasattr(record, "to_dict"):
                result.append(record.to_dict())
            elif isinstance(record, dict):
                result.append(record)
            else:
                result.append({"value": str(record)})
        return result
