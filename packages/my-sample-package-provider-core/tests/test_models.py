"""Tests for core.models module."""

from datetime import datetime

import pytest

from core.models import DataModel


@pytest.fixture
def sample_record() -> dict:
    return {
        "id": "rec-001",
        "name": "Sample Record",
        "value": 42.0,
        "tags": ["test", "sample"],
        "created_at": "2026-01-01T00:00:00",
    }


@pytest.fixture
def sample_model(sample_record) -> DataModel:
    return DataModel.from_dict(sample_record)


def test_from_dict(sample_record):
    model = DataModel.from_dict(sample_record)
    assert model.id == "rec-001"
    assert model.name == "Sample Record"
    assert model.value == 42.0
    assert model.tags == ["test", "sample"]


def test_to_dict_roundtrip(sample_model):
    data = sample_model.to_dict()
    restored = DataModel.from_dict(data)
    assert restored.id == sample_model.id
    assert restored.name == sample_model.name
    assert restored.value == sample_model.value
    assert restored.tags == sample_model.tags


def test_default_tags_is_empty_list():
    model = DataModel(id="x", name="X", value=0.0)
    assert model.tags == []


def test_default_created_at_is_datetime():
    model = DataModel(id="x", name="X", value=0.0)
    assert isinstance(model.created_at, datetime)


def test_to_dict_created_at_is_isoformat(sample_model):
    data = sample_model.to_dict()
    assert isinstance(data["created_at"], str)
    datetime.fromisoformat(data["created_at"])  # should not raise
