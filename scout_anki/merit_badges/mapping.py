"""Image mapping and selection logic."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..log import get_logger
from ..schema import Badge, slug


@lru_cache(maxsize=128)
def _cached_slug(name: str) -> str:
    """Cached version of slug generation for performance."""
    return slug(name)


def find_image_for_badge(badge: Badge, available_images: dict[str, bytes]) -> str | None:
    """Find the best matching image for a badge.

    Args:
        badge: Badge to find image for
        available_images: Dict mapping image basename to content

    Returns:
        Image basename if found, None otherwise
    """
    logger = get_logger()

    # If badge specifies an image, try to match by basename
    if badge.image:
        # Try exact match first
        if badge.image in available_images:
            logger.debug(f"Exact image match for {badge.name}: {badge.image}")
            return badge.image

        # Try matching by basename
        badge_basename = os.path.basename(badge.image)
        if badge_basename in available_images:
            logger.debug(f"Basename image match for {badge.name}: {badge_basename}")
            return badge_basename

    # Infer image from badge name using slug rules
    badge_slug = _cached_slug(badge.name)

    # Look for pattern: <slug>-merit-badge.* or <slug>-<version>-merit-badge.*
    merit_badge_pattern = f"{badge_slug}-merit-badge"
    candidates = []

    for image_name in available_images.keys():
        image_stem = Path(image_name).stem.lower()

        # Check if it matches the merit badge pattern
        if image_stem == merit_badge_pattern:
            candidates.append(image_name)
        # Check for versioned pattern: <slug>-<number>-merit-badge
        elif image_stem.startswith(f"{badge_slug}-") and image_stem.endswith("-merit-badge"):
            # Extract the middle part to see if it's a version number
            middle_part = image_stem[len(f"{badge_slug}-") : -len("-merit-badge")]
            if middle_part.isdigit():
                candidates.append(image_name)
        # Also check for exact slug match
        elif image_stem == badge_slug:
            candidates.append(image_name)

    if candidates:
        # If multiple candidates, choose the one with shortest basename
        best_candidate = min(candidates, key=len)
        logger.debug(f"Inferred image for {badge.name}: {best_candidate}")
        return best_candidate

    logger.debug(f"No image found for badge: {badge.name}")
    return None


def map_badges_to_images(
    badges: list[Badge], available_images: dict[str, bytes]
) -> tuple[list[tuple[Badge, str]], list[Badge]]:
    """Map badges to their corresponding images.

    Args:
        badges: List of badges to map
        available_images: Dict mapping image basename to content

    Returns:
        Tuple of (successful mappings, badges without images)
    """
    logger = get_logger()

    mapped_badges = []
    unmapped_badges = []

    for badge in badges:
        image_name = find_image_for_badge(badge, available_images)

        if image_name:
            mapped_badges.append((badge, image_name))
        else:
            unmapped_badges.append(badge)

    logger.info(
        f"Mapped {len(mapped_badges)} badges to images, "
        f"{len(unmapped_badges)} badges without images"
    )

    return mapped_badges, unmapped_badges


def get_unused_images(
    badges: list[Badge], available_images: dict[str, bytes], mapped_images: set[str]
) -> list[str]:
    """Get list of images that weren't used by any badge.

    Args:
        badges: List of all badges
        available_images: Dict of all available images
        mapped_images: Set of image names that were used

    Returns:
        List of unused image names
    """
    all_images = set(available_images.keys())
    unused = all_images - mapped_images
    return sorted(unused)


def generate_expected_image_name(badge: Badge) -> str:
    """Generate the expected image filename for a badge.

    Args:
        badge: Badge to generate filename for

    Returns:
        Expected image filename
    """
    if badge.image:
        return os.path.basename(badge.image)

    badge_slug = slug(badge.name)
    return f"{badge_slug}-merit-badge.jpg"


def create_mapping_summary(
    badges: list[Badge],
    available_images: dict[str, bytes],
    mapped_badges: list[tuple[Badge, str]],
    unmapped_badges: list[Badge],
) -> dict[str, Any]:
    """Create a summary of the mapping process.

    Args:
        badges: All badges
        available_images: All available images
        mapped_badges: Successfully mapped badges
        unmapped_badges: Badges without images

    Returns:
        Summary dict with counts and details
    """
    mapped_image_names = {img_name for _, img_name in mapped_badges}
    unused_images = get_unused_images(badges, available_images, mapped_image_names)

    # Create missing image details
    missing_images = []
    for badge in unmapped_badges:
        expected = generate_expected_image_name(badge)
        missing_images.append({"badge_name": badge.name, "expected_image": expected})

    return {
        "total_badges": len(badges),
        "total_images": len(available_images),
        "mapped_badges": len(mapped_badges),
        "unmapped_badges": len(unmapped_badges),
        "unused_images": len(unused_images),
        "missing_image_details": missing_images,
        "unused_image_names": unused_images,
    }
