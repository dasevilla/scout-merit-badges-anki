"""Cub Scout adventure processing."""

import json
from dataclasses import dataclass
from pathlib import Path

from ..log import get_logger


@dataclass
class Adventure:
    """Cub Scout adventure data structure."""

    name: str
    rank: str
    type: str  # Required/Elective
    overview: str
    image_name: str | None = None

    @property
    def slug(self) -> str:
        """Generate slug for image matching."""
        return self.name.lower().replace(" ", "-").replace("'", "")

    @property
    def stable_id(self) -> int:
        """Generate stable ID for Anki."""
        return abs(hash(f"adventure:{self.rank}:{self.name}")) % (2**31)


def normalize_adventure_data(data: dict) -> Adventure:
    """Convert JSON adventure data to Adventure object."""
    return Adventure(
        name=data.get("adventure_name", ""),
        rank=data.get("rank_name", ""),
        type=data.get("adventure_type", ""),
        overview=data.get("adventure_overview", ""),
    )


def process_adventure_directory(directory_path: str) -> tuple[list[Adventure], dict[str, Path]]:
    """Process directory for Cub Scout adventures and images."""
    logger = get_logger()
    directory = Path(directory_path)

    adventures = []
    available_images = {}

    # Find all adventure JSON files in rank directories
    rank_dirs = ["lion", "tiger", "wolf", "bear", "webelos", "arrow-of-light"]

    for rank_dir in rank_dirs:
        rank_path = directory / rank_dir
        if not rank_path.exists():
            continue

        logger.debug(f"Processing rank directory: {rank_path}")

        # Process JSON files
        for json_file in rank_path.glob("*.json"):
            if json_file.name.startswith("bobcat"):
                continue  # Skip bobcat files

            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                    adventure = normalize_adventure_data(data)
                    if adventure.name:  # Only add if we have a name
                        adventures.append(adventure)
                        logger.debug(f"Added adventure: {adventure.name} ({adventure.rank})")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse {json_file}: {e}")

        # Process images
        images_dir = rank_path / "images"
        if images_dir.exists():
            for image_file in images_dir.glob("*"):
                if image_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif"}:
                    available_images[image_file.name] = image_file
                    logger.debug(f"Found image: {image_file.name}")

    logger.info(f"Found {len(adventures)} adventures and {len(available_images)} images")
    return adventures, available_images


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
