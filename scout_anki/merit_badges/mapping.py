"""Image mapping and selection logic."""

from typing import Any

from ..log import get_logger


def find_image_for_badge(badge: Any, available_images: dict[str, Any]) -> str | None:
    """Find the image for a badge using the image_filename field.

    Args:
        badge: Badge to find image for
        available_images: Dict mapping image basename to path

    Returns:
        Image basename if found, None otherwise
    """
    logger = get_logger()

    # Use the image_filename field directly
    if hasattr(badge, "image_filename") and badge.image_filename:
        if badge.image_filename in available_images:
            logger.debug(f"Direct image match for {badge.name}: {badge.image_filename}")
            return badge.image_filename

    logger.debug(f"No image found for badge: {badge.name}")
    return None


def map_badges_to_images(
    badges: list[Any], available_images: dict[str, Any]
) -> tuple[list[tuple[Any, str]], list[Any]]:
    """Map badges to their corresponding images.

    Args:
        badges: List of badges to map
        available_images: Dict mapping image basename to path

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


def create_mapping_summary(
    badges: list[Any],
    available_images: dict[str, Any],
    mapped_badges: list[tuple[Any, str]],
    unmapped_badges: list[Any],
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
    unused_images = set(available_images.keys()) - mapped_image_names

    # Create missing image details
    missing_images = []
    for badge in unmapped_badges:
        expected = getattr(badge, "image_filename", "unknown")
        missing_images.append({"badge_name": badge.name, "expected_image": expected})

    return {
        "total_badges": len(badges),
        "total_images": len(available_images),
        "mapped_badges": len(mapped_badges),
        "unmapped_badges": len(unmapped_badges),
        "unused_images": len(unused_images),
        "missing_image_details": missing_images,
    }
