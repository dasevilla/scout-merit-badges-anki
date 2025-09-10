"""Merit badge processor."""

import json
from pathlib import Path
from typing import Any

import click

from .. import deck
from ..log import get_logger
from ..processor import DeckProcessor
from .schema import normalize_badge_data


class MeritBadgeProcessor(DeckProcessor):
    """Processor for merit badge decks."""

    def __init__(self):
        super().__init__("badges")

    def get_defaults(self) -> dict[str, str]:
        """Get default values for merit badges."""
        return {
            "out": "merit_badges.apkg",
            "deck_name": "Merit Badges",
            "model_name": "Merit Badge Quiz",
        }

    def process_directory(self, directory_path: str) -> tuple[list[Any], dict[str, Any]]:
        """Process directory to find badges and images."""
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
        badges = normalize_badge_data(all_badge_data)

        # Find image files
        available_images = {}
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

        for img_file in directory.glob("**/*"):
            if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                available_images[img_file.name] = img_file

        return badges, available_images

    def map_content_to_images(
        self, content: list[Any], images: dict[str, Any]
    ) -> tuple[list[tuple[Any, str]], list[Any]]:
        """Map badges to images."""
        logger = get_logger()
        mapped_badges = []
        unmapped_badges = []

        for badge in content:
            # Use the image_filename field directly
            image_name = None
            if hasattr(badge, "image_filename") and badge.image_filename:
                if badge.image_filename in images:
                    image_name = badge.image_filename

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
        self,
        content: list[Any],
        images: dict[str, Any],
        mapped: list[tuple[Any, str]],
        unmapped: list[Any],
    ) -> dict[str, Any]:
        """Create mapping summary for badges."""
        mapped_image_names = {img_name for _, img_name in mapped}
        unused_images = set(images.keys()) - mapped_image_names

        # Create missing image details
        missing_images = []
        for badge in unmapped:
            expected = getattr(badge, "image_filename", "unknown")
            missing_images.append({"badge_name": badge.name, "expected_image": expected})

        return {
            "total_badges": len(content),
            "total_images": len(images),
            "mapped_badges": len(mapped),
            "unmapped_badges": len(unmapped),
            "unused_images": len(unused_images),
            "missing_image_details": missing_images,
        }

    def print_summary(self, summary: dict[str, Any], dry_run: bool) -> None:
        """Print merit badge summary."""
        click.echo("\n" + "=" * 60)
        click.echo("BUILD SUMMARY")
        click.echo("=" * 60)

        click.echo(f"Total badges in JSON: {summary['total_badges']}")
        click.echo(f"Total images available: {summary['total_images']}")
        click.echo(f"Badges mapped to images: {summary['mapped_badges']}")
        click.echo(f"Badges without images: {summary['unmapped_badges']}")
        click.echo(f"Unused images: {summary['unused_images']}")

        if summary["missing_image_details"]:
            click.echo(f"\nMissing images ({len(summary['missing_image_details'])}):")
            for item in summary["missing_image_details"]:
                click.echo(f"  • {item['badge_name']} → {item['expected_image']}")

        if dry_run:
            click.echo(f"\n[DRY RUN] Would create deck with {summary['mapped_badges']} notes")

        click.echo("=" * 60)

    def create_deck(
        self,
        deck_name: str,
        model_name: str,
        mapped_content: list[tuple[Any, str]],
        images: dict[str, Any],
    ) -> tuple[Any, list[str]]:
        """Create merit badge deck."""
        return deck.create_merit_badge_deck(deck_name, model_name, mapped_content, images)
