"""Adventure processor."""

from pathlib import Path

import click
import genanki

from .. import deck
from ..image_utils import map_content_by_image_filename
from ..log import get_logger
from ..processor import DeckProcessor
from .schema import Adventure, process_adventure_directory


class AdventureProcessor(DeckProcessor):
    """Processor for Cub Scout adventure decks."""

    def __init__(self):
        super().__init__("adventures")

    def get_defaults(self) -> dict[str, str]:
        """Get default values for adventures."""
        return {
            "out": "cub_scout_adventure_image_trainer.apkg",
            "deck_name": "Cub Scout Adventure Image Trainer",
            "model_name": "Cub Scout Adventure Quiz",
        }

    def process_directory(self, directory_path: str) -> tuple[list[Adventure], dict[str, Path]]:
        """Process directory for adventures."""
        return process_adventure_directory(directory_path)

    def map_content_to_images(
        self, content: list[Adventure], images: dict[str, Path]
    ) -> tuple[list[tuple[Adventure, str]], list[Adventure]]:
        """Map adventures to images."""
        logger = get_logger()
        mapped_adventures, unmapped_adventures = map_content_by_image_filename(content, images)

        logger.info(
            f"Mapped {len(mapped_adventures)} adventures to images, "
            f"{len(unmapped_adventures)} adventures without images"
        )
        return mapped_adventures, unmapped_adventures

    def create_mapping_summary(
        self,
        content: list[Adventure],
        images: dict[str, Path],
        mapped: list[tuple[Adventure, str]],
        unmapped: list[Adventure],
    ) -> dict[str, int | list[str]]:
        """Create mapping summary for adventures."""
        used_images = {image_name for _, image_name in mapped}
        unused_images = set(images.keys()) - used_images

        missing_image_details = []
        for adventure in unmapped:
            expected = getattr(adventure, "image_filename", f"{adventure.slug}.jpg")
            missing_image_details.append(
                {
                    "adventure_name": f"{adventure.name} ({adventure.rank})",
                    "expected_image": expected,
                }
            )

        return {
            "total_adventures": len(content),
            "total_images": len(images),
            "mapped_adventures": len(mapped),
            "unmapped_adventures": len(unmapped),
            "unused_images": len(unused_images),
            "missing_image_details": missing_image_details,
        }

    def print_summary(self, summary: dict[str, int | list[str]], dry_run: bool) -> None:
        """Print adventure summary."""
        click.echo("\n" + "=" * 60)
        click.echo("BUILD SUMMARY")
        click.echo("=" * 60)

        click.echo(f"Total adventures in JSON: {summary['total_adventures']}")
        click.echo(f"Total images available: {summary['total_images']}")
        click.echo(f"Adventures mapped to images: {summary['mapped_adventures']}")
        click.echo(f"Adventures without images: {summary['unmapped_adventures']}")
        click.echo(f"Unused images: {summary['unused_images']}")

        if summary["missing_image_details"]:
            click.echo(f"\nMissing images ({len(summary['missing_image_details'])}):")
            for item in summary["missing_image_details"]:
                click.echo(f"  • {item['adventure_name']} → {item['expected_image']}")

        if dry_run:
            click.echo(f"\n[DRY RUN] Would create deck with {summary['mapped_adventures']} notes")

        click.echo("=" * 60)

    def create_deck(
        self,
        deck_name: str,
        model_name: str,
        mapped_content: list[tuple[Adventure, str]],
        images: dict[str, Path],
    ) -> tuple[genanki.Deck, list[str]]:
        """Create adventure deck."""
        return deck.create_adventure_deck(deck_name, model_name, mapped_content, images)
