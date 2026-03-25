"""Data models for the core package."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DataModel:
    """A simple data model representing a generic record."""

    id: str
    name: str
    value: float
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Serialize the model to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DataModel":
        """Deserialize a model from a dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            id=data["id"],
            name=data["name"],
            value=data["value"],
            tags=data.get("tags", []),
            created_at=created_at or datetime.now(),
        )
