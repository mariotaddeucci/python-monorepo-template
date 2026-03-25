"""Tests for standalone.text module."""

from standalone.text import slugify, truncate


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"


def test_slugify_special_chars():
    assert slugify("Hello World!") == "hello-world"


def test_slugify_multiple_spaces():
    assert slugify("hello   world") == "hello-world"


def test_slugify_underscores():
    assert slugify("hello_world") == "hello-world"


def test_slugify_leading_trailing_spaces():
    assert slugify("  hello  ") == "hello"


def test_slugify_already_slug():
    assert slugify("hello-world") == "hello-world"


def test_truncate_no_cut():
    assert truncate("Hello", 10) == "Hello"


def test_truncate_exact_length():
    assert truncate("Hello", 5) == "Hello"


def test_truncate_cut_with_default_suffix():
    assert truncate("Hello World", 8) == "Hello..."


def test_truncate_custom_suffix():
    assert truncate("Hello World", 7, suffix="…") == "Hello …"


def test_truncate_empty_string():
    assert truncate("", 5) == ""


def test_truncate_suffix_longer_than_max():
    # When text is shorter than max_length, no truncation
    assert truncate("Hi", 10) == "Hi"
