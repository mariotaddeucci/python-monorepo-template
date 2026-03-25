"""Text utility functions."""

import re


def slugify(text: str) -> str:
    """Convert a string into a URL-friendly slug.

    Args:
        text: Input string.

    Returns:
        Lowercase slug with hyphens instead of spaces/special chars.

    Example:
        >>> slugify("Hello World!")
        'hello-world'
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to a maximum length, appending a suffix if cut.

    Args:
        text: Input string.
        max_length: Maximum allowed length (including suffix).
        suffix: String appended when truncation occurs.

    Returns:
        Truncated string.

    Example:
        >>> truncate("Hello World", 8)
        'Hello...'
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
