"""Cub Scout adventure processing."""

import json
from dataclasses import dataclass
from pathlib import Path

from ..image_utils import discover_images
from ..log import get_logger


@dataclass
class Adventure:
    """Cub Scout adventure data structure."""

    name: str
    rank: str
    type: str  # Required/Elective
    overview: str
    image_filename: str | None = None

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
        image_filename=data.get("image_filename"),
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
            rank_images = discover_images(images_dir)
            available_images.update(rank_images)
            logger.debug(f"Found {len(rank_images)} images in {images_dir}")

    logger.info(f"Found {len(adventures)} adventures and {len(available_images)} images")
    return adventures, available_images
