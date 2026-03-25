"""Math utility functions."""


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max.

    Args:
        value: The value to clamp.
        min_value: Lower bound (inclusive).
        max_value: Upper bound (inclusive).

    Returns:
        The clamped value.

    Example:
        >>> clamp(15, 0, 10)
        10
        >>> clamp(-3, 0, 10)
        0
    """
    return max(min_value, min(max_value, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t.

    Args:
        a: Start value.
        b: End value.
        t: Interpolation factor in [0, 1].

    Returns:
        Interpolated value.

    Example:
        >>> lerp(0, 10, 0.5)
        5.0
    """
    return a + (b - a) * t
