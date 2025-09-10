"""Merit badge processor."""

from typing import Any

import click

from . import deck, directory, mapping
from .processor import DeckProcessor


class MeritBadgeProcessor(DeckProcessor):
    """Processor for merit badge decks."""

    def __init__(self):
        super().__init__("badges")

    def get_defaults(self) -> dict[str, str]:
        """Get default values for merit badges."""
        return {
            "out": "merit_badges_image_trainer.apkg",
            "deck_name": "Merit Badges Visual Trainer",
            "model_name": "Merit Badge Image → Text",
        }

    def process_directory(self, directory_path: str) -> tuple[list[Any], dict[str, Any]]:
        """Process directory for merit badges."""
        return directory.process_directory(directory_path)

    def map_content_to_images(
        self, content: list[Any], images: dict[str, Any]
    ) -> tuple[list[tuple[Any, str]], list[Any]]:
        """Map badges to images."""
        return mapping.map_badges_to_images(content, images)

    def create_mapping_summary(
        self,
        content: list[Any],
        images: dict[str, Any],
        mapped: list[tuple[Any, str]],
        unmapped: list[Any],
    ) -> dict[str, Any]:
        """Create mapping summary for badges."""
        return mapping.create_mapping_summary(content, images, mapped, unmapped)

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
