"""Adventure processor."""

from typing import Any

import click

from .. import deck
from ..processor import DeckProcessor
from . import adventure


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

    def process_directory(self, directory_path: str) -> tuple[list[Any], dict[str, Any]]:
        """Process directory for adventures."""
        return adventure.process_adventure_directory(directory_path)

    def map_content_to_images(
        self, content: list[Any], images: dict[str, Any]
    ) -> tuple[list[tuple[Any, str]], list[Any]]:
        """Map adventures to images."""
        return adventure.map_adventures_to_images(content, images)

    def create_mapping_summary(
        self,
        content: list[Any],
        images: dict[str, Any],
        mapped: list[tuple[Any, str]],
        unmapped: list[Any],
    ) -> dict[str, Any]:
        """Create mapping summary for adventures."""
        return adventure.create_adventure_mapping_summary(content, images, mapped, unmapped)

    def print_summary(self, summary: dict[str, Any], dry_run: bool) -> None:
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
        mapped_content: list[tuple[Any, str]],
        images: dict[str, Any],
    ) -> tuple[Any, list[str]]:
        """Create adventure deck."""
        return deck.create_adventure_deck(deck_name, model_name, mapped_content, images)
