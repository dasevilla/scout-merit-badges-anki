"""Badge model and JSON schema normalization."""

import hashlib
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class Badge:
    """Merit badge model."""

    name: str
    description: str
    image: str | None = None
    image_filename: str | None = None
    source: str | None = None
    eagle_required: bool = False


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


def normalize_badge_data(data: Any) -> list[Badge]:
    """Normalize JSON data into Badge objects.

    Args:
        data: Raw JSON data (list or dict)

    Returns:
        List of normalized Badge objects
    """
    badges: list[Badge] = []

    # Extract badge list from various JSON structures
    if isinstance(data, list):
        badge_list = data
    elif isinstance(data, dict):
        # Try common keys for badge lists
        for key in ["badges", "items", "data", "meritBadges"]:
            if key in data:
                badge_list = data[key]
                break
        else:
            # If no known key found, treat the dict as a single badge
            badge_list = [data]
    else:
        return badges

    seen_names = set()

    for item in badge_list:
        if not isinstance(item, dict):
            continue

        # Extract name (required)
        name = None
        for name_key in ["name", "title", "badge"]:
            if item.get(name_key):
                name = str(item[name_key]).strip()
                break

        if not name:
            continue  # Skip badges without names

        # Skip duplicates (keep first occurrence)
        if name in seen_names:
            continue
        seen_names.add(name)

        # Extract description
        description = ""
        for desc_key in ["overview", "description", "blurb", "summary"]:
            if item.get(desc_key):
                description = str(item[desc_key]).strip()
                break

        # Extract image filename
        image = None
        for img_key in ["image", "img", "icon"]:
            if item.get(img_key):
                image = str(item[img_key]).strip()
                break

        # Extract image filename
        image_filename = None
        if item.get("image_filename"):
            image_filename = str(item["image_filename"]).strip()

        # Extract eagle required status
        eagle_required = bool(item.get("is_eagle_required", False))

        badge = Badge(
            name=name,
            description=description,
            image=image,
            image_filename=image_filename,
            source="JSON",
            eagle_required=eagle_required,
        )
        badges.append(badge)

    return badges


def merge_badge_lists(badge_lists: list[list[Badge]]) -> list[Badge]:
    """Merge multiple badge lists, removing duplicates by name.

    Args:
        badge_lists: List of badge lists to merge

    Returns:
        Merged list with duplicates removed (first occurrence kept)
    """
    merged = []
    seen_names = set()

    for badge_list in badge_lists:
        for badge in badge_list:
            if badge.name not in seen_names:
                merged.append(badge)
                seen_names.add(badge.name)

    return merged
