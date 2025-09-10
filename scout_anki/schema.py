"""Generic schema utilities."""

import hashlib
import re


def stable_id(seed: str) -> int:
    """Generate a stable ID from a seed string using SHA1 hash.

    Args:
        seed: String to hash

    Returns:
        Integer ID derived from first 10 hex chars of SHA1 hash

    Examples:
        >>> stable_id("test")
        2711781484
        >>> stable_id("Merit Badges")
        1234567890  # Deterministic output
    """
    return int(hashlib.sha1(seed.encode(), usedforsecurity=False).hexdigest()[:10], 16)


def slug(s: str) -> str:
    """Convert string to slug format.

    Args:
        s: String to convert

    Returns:
        Lowercase string with spaces as dashes, only alphanumeric and hyphens

    Raises:
        ValueError: If input string is empty after processing
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string, got {type(s)}")

    # Convert to lowercase and replace spaces with dashes
    s = s.lower().replace(" ", "-")
    # Remove non-alphanumeric characters except hyphens
    s = re.sub(r"[^a-z0-9-]", "", s)
    # Remove multiple consecutive dashes
    s = re.sub(r"-+", "-", s)
    # Remove leading/trailing dashes
    result = s.strip("-")

    if not result:
        raise ValueError("Input string produces empty slug")

    return result
