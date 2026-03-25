"""Tests for the my-sample-package proxy."""

import importlib

import pytest


def test_version_attribute_exists():
    import my_sample_package

    assert hasattr(my_sample_package, "__version__")
    assert isinstance(my_sample_package.__version__, str)


def test_proxy_exposes_core_symbols():
    import my_sample_package as msp

    # core is a workspace dep — should be importable
    assert hasattr(msp, "DataModel")
    assert hasattr(msp, "format_message")
    assert hasattr(msp, "process_data")


def test_proxy_exposes_standalone_symbols():
    import my_sample_package as msp

    assert hasattr(msp, "clamp")
    assert hasattr(msp, "lerp")
    assert hasattr(msp, "slugify")
    assert hasattr(msp, "truncate")


def test_proxy_getattr_missing_raises_attribute_error():
    import my_sample_package as msp

    with pytest.raises(AttributeError, match="nonexistent_symbol_xyz"):
        _ = msp.nonexistent_symbol_xyz


def test_dir_includes_known_symbols():
    import my_sample_package as msp

    d = dir(msp)
    assert "__version__" in d


def test_proxy_datamodel_usable():
    import my_sample_package as msp

    DataModel = msp.DataModel  # type: ignore[attr-defined]
    obj = DataModel(id=42, name="proxy-test", value=3.14)
    assert obj.id == 42
    assert obj.name == "proxy-test"
    assert obj.value == 3.14


def test_proxy_clamp_usable():
    import my_sample_package as msp

    assert msp.clamp(15, 0, 10) == 10  # type: ignore[attr-defined]
    assert msp.clamp(-5, 0, 10) == 0  # type: ignore[attr-defined]
    assert msp.clamp(5, 0, 10) == 5  # type: ignore[attr-defined]


def test_module_reloads_cleanly():
    import my_sample_package

    reloaded = importlib.reload(my_sample_package)
    assert hasattr(reloaded, "__version__")
