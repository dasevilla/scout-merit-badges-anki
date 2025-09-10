"""Adventure image mapping logic."""

from pathlib import Path

from ..log import get_logger
from .adventure import Adventure


def map_adventures_to_images(
    adventures: list[Adventure], available_images: dict[str, Path]
) -> tuple[list[tuple[Adventure, str]], list[Adventure]]:
    """Map adventures to their corresponding images."""
    logger = get_logger()
    mapped_adventures = []
    unmapped_adventures = []

    for adventure in adventures:
        image_name = find_adventure_image(adventure, available_images)
        if image_name:
            mapped_adventures.append((adventure, image_name))
            logger.debug(f"Mapped {adventure.name} → {image_name}")
        else:
            unmapped_adventures.append(adventure)
            logger.debug(f"No image found for {adventure.name}")

    logger.info(
        f"Mapped {len(mapped_adventures)} adventures to images, "
        f"{len(unmapped_adventures)} adventures without images"
    )
    return mapped_adventures, unmapped_adventures


def find_adventure_image(adventure: Adventure, available_images: dict[str, Path]) -> str | None:
    """Find the best matching image for an adventure."""
    # Try exact slug match first
    slug = adventure.slug
    for image_name in available_images:
        image_base = Path(image_name).stem.lower()
        if image_base == slug:
            return image_name

    # Try partial matches
    for image_name in available_images:
        image_base = Path(image_name).stem.lower()
        if slug in image_base or image_base in slug:
            return image_name

    return None


def create_adventure_mapping_summary(
    adventures: list[Adventure],
    available_images: dict[str, Path],
    mapped_adventures: list[tuple[Adventure, str]],
    unmapped_adventures: list[Adventure],
) -> dict:
    """Create summary of adventure mapping results."""
    used_images = {image_name for _, image_name in mapped_adventures}
    unused_images = set(available_images.keys()) - used_images

    missing_image_details = []
    for adventure in unmapped_adventures:
        missing_image_details.append(
            {
                "adventure_name": f"{adventure.name} ({adventure.rank})",
                "expected_image": f"{adventure.slug}.jpg",
            }
        )

    return {
        "total_adventures": len(adventures),
        "total_images": len(available_images),
        "mapped_adventures": len(mapped_adventures),
        "unmapped_adventures": len(unmapped_adventures),
        "unused_images": len(unused_images),
        "missing_image_details": missing_image_details,
    }
