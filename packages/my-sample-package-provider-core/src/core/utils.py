"""Utility functions for the core package."""

from core.models import DataModel


def format_message(template: str, **kwargs) -> str:
    """Format a message string with given keyword arguments.

    Args:
        template: A string template with {key} placeholders.
        **kwargs: Values to substitute into the template.

    Returns:
        The formatted string.

    Example:
        >>> format_message("Hello, {name}!", name="World")
        'Hello, World!'
    """
    return template.format(**kwargs)


def process_data(records: list[dict]) -> list[DataModel]:
    """Convert a list of raw dicts into DataModel instances.

    Args:
        records: A list of dictionaries with record data.

    Returns:
        A list of DataModel instances.
    """
    return [DataModel.from_dict(record) for record in records]


def filter_by_tag(models: list[DataModel], tag: str) -> list[DataModel]:
    """Filter a list of DataModel instances by a specific tag.

    Args:
        models: List of DataModel instances.
        tag: The tag to filter by.

    Returns:
        A filtered list containing only models with the given tag.
    """
    return [m for m in models if tag in m.tags]
