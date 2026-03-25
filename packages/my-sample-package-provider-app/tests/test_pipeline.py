"""Tests for app.pipeline module."""

import pytest

from app.pipeline import Pipeline


@pytest.fixture
def raw_records() -> list[dict]:
    return [
        {"id": "1", "name": "Alpha", "value": 10.0, "tags": ["a", "b"]},
        {"id": "2", "name": "Beta", "value": 20.0, "tags": ["b", "c"]},
        {"id": "3", "name": "Gamma", "value": 30.0, "tags": ["c"]},
    ]


def test_pipeline_name():
    p = Pipeline("my-pipeline")
    assert p.name == "my-pipeline"


def test_load_returns_self(raw_records):
    p = Pipeline("test")
    result = p.load(raw_records)
    assert result is p


def test_count_after_load(raw_records):
    p = Pipeline("test").load(raw_records)
    assert p.count() == 3


def test_results_after_load(raw_records):
    p = Pipeline("test").load(raw_records)
    assert len(p.results()) == 3


def test_load_empty():
    p = Pipeline("test").load([])
    assert p.count() == 0
    assert p.results() == []


def test_results_is_copy(raw_records):
    p = Pipeline("test").load(raw_records)
    r1 = p.results()
    r1.append("extra")
    assert p.count() == 3  # internal state unchanged


def test_has_core_attribute():
    p = Pipeline("test")
    assert isinstance(p.has_core, bool)


def test_filter_tag_without_core_raises(raw_records):
    p = Pipeline("test").load(raw_records)
    if not p.has_core:
        with pytest.raises(RuntimeError, match="core"):
            p.filter_tag("a")


def test_filter_tag_with_core(raw_records):
    p = Pipeline("test").load(raw_records)
    if p.has_core:
        p.filter_tag("b")
        assert p.count() == 2


def test_load_with_core_returns_typed_objects(raw_records):
    p = Pipeline("test").load(raw_records)
    if p.has_core:
        from core.models import DataModel

        assert all(isinstance(r, DataModel) for r in p.results())
    else:
        assert all(isinstance(r, dict) for r in p.results())
