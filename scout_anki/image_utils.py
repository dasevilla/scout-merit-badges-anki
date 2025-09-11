"""Shared image processing utilities."""

from pathlib import Path
from typing import Protocol

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


class ContentItem(Protocol):
    """Protocol for content items that can be mapped to images."""

    image_filename: str | None


def discover_images(directory: Path) -> dict[str, Path]:
    """Discover all image files in directory and subdirectories."""
    available_images = {}
    for img_file in directory.glob("**/*"):
        if img_file.is_file() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
            available_images[img_file.name] = img_file
    return available_images


def map_content_by_image_filename(
    content: list[ContentItem], images: dict[str, Path]
) -> tuple[list[tuple[ContentItem, str]], list[ContentItem]]:
    """Map content to images using image_filename field."""
    mapped = []
    unmapped = []

    for item in content:
        image_name = None
        if hasattr(item, "image_filename") and item.image_filename:
            if item.image_filename in images:
                image_name = item.image_filename

        if image_name:
            mapped.append((item, image_name))
        else:
            unmapped.append(item)

    return mapped, unmapped
