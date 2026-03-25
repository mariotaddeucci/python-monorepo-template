"""Tests for core.utils module."""

import pytest

from core.models import DataModel
from core.utils import filter_by_tag, format_message, process_data


def test_format_message_simple_substitution():
    result = format_message("Hello, {name}!", name="World")
    assert result == "Hello, World!"


def test_format_message_multiple_placeholders():
    result = format_message("{greeting}, {name}! You have {count} messages.", greeting="Hi", name="Alice", count=3)
    assert result == "Hi, Alice! You have 3 messages."


def test_format_message_no_placeholders():
    result = format_message("No placeholders here.")
    assert result == "No placeholders here."


def test_format_message_missing_key_raises():
    with pytest.raises(KeyError):
        format_message("Hello, {name}!")


def test_process_data_converts_dicts_to_models():
    records = [
        {"id": "1", "name": "First", "value": 1.0},
        {"id": "2", "name": "Second", "value": 2.0},
    ]
    models = process_data(records)
    assert len(models) == 2
    assert all(isinstance(m, DataModel) for m in models)


def test_process_data_empty_list():
    assert process_data([]) == []


def test_filter_by_tag_filters_correctly():
    models = [
        DataModel(id="1", name="A", value=1.0, tags=["alpha", "beta"]),
        DataModel(id="2", name="B", value=2.0, tags=["beta"]),
        DataModel(id="3", name="C", value=3.0, tags=["gamma"]),
    ]
    result = filter_by_tag(models, "beta")
    assert len(result) == 2
    assert all("beta" in m.tags for m in result)


def test_filter_by_tag_no_match_returns_empty():
    models = [DataModel(id="1", name="A", value=1.0, tags=["alpha"])]
    result = filter_by_tag(models, "nonexistent")
    assert result == []
