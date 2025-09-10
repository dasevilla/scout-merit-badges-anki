"""Directory processing for scout-merit-badges-anki."""

import json
from pathlib import Path

from .. import schema


def process_directory(directory_path):
    """Process extracted directory to find badges and images.

    Args:
        directory_path: Path to directory containing extracted files

    Returns:
        tuple: (badges, available_images) where:
            - badges: List of normalized badge objects
            - available_images: Dict mapping image names to file paths
    """
    directory = Path(directory_path)

    # Find and process JSON files
    all_badge_data = []
    for json_file in directory.glob("**/*.json"):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        # Handle both single objects and arrays
        if isinstance(data, list):
            all_badge_data.extend(data)
        else:
            all_badge_data.append(data)

    # Normalize all badge data
    badges = schema.normalize_badge_data(all_badge_data)

    # Find image files
    available_images = {}
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    for img_file in directory.glob("**/*"):
        if img_file.is_file() and img_file.suffix.lower() in image_extensions:
            available_images[img_file.name] = img_file

    return badges, available_images
