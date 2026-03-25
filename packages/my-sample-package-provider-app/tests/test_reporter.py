"""Tests for app.reporter module."""

import pytest

from app.reporter import Reporter


@pytest.fixture
def reporter() -> Reporter:
    return Reporter(title="Test Report")


@pytest.fixture
def dict_records() -> list[dict]:
    return [
        {"id": "1", "name": "Alpha", "value": 10.0, "tags": ["a"]},
        {"id": "2", "name": "Beta", "value": 20.0, "tags": []},
    ]


def test_default_title():
    r = Reporter()
    assert r.title == "Report"


def test_custom_title():
    r = Reporter("My Report")
    assert r.title == "My Report"


def test_summary_contains_title(reporter, dict_records):
    output = reporter.summary(dict_records)
    assert "Test Report" in output


def test_summary_contains_record_count(reporter, dict_records):
    output = reporter.summary(dict_records)
    assert "Total records: 2" in output


def test_summary_contains_record_names(reporter, dict_records):
    output = reporter.summary(dict_records)
    assert "Alpha" in output
    assert "Beta" in output


def test_summary_shows_tags(reporter, dict_records):
    output = reporter.summary(dict_records)
    assert "[a]" in output


def test_summary_empty_list(reporter):
    output = reporter.summary([])
    assert "Total records: 0" in output


def test_as_dicts_with_dicts(reporter, dict_records):
    result = reporter.as_dicts(dict_records)
    assert result == dict_records


def test_as_dicts_with_model_like_objects(reporter):
    class FakeModel:
        def to_dict(self):
            return {"name": "Fake", "value": 99.0}

    result = reporter.as_dicts([FakeModel()])
    assert result == [{"name": "Fake", "value": 99.0}]


def test_as_dicts_empty(reporter):
    assert reporter.as_dicts([]) == []


def test_summary_with_core_models(reporter):
    """When core is available, DataModel objects are accepted."""
    try:
        from core.models import DataModel

        model = DataModel(id="x", name="CoreRecord", value=7.5, tags=["core"])
        output = reporter.summary([model])
        assert "CoreRecord" in output
        assert "7.5" in output
    except ImportError:
        pytest.skip("core not installed")
