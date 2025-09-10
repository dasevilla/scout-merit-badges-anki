"""Command line interface for scout-merit-badges-anki."""

import sys

import click

from . import deck, directory, mapping
from .errors import (
    NoBadgesFoundError,
)
from .log import setup_logging


@click.group()
def cli():
    """Scout Archive to Anki deck tools."""
    pass


@cli.command()
@click.argument("directory_path", type=click.Path(exists=True, file_okay=False, readable=True))
@click.option(
    "--out",
    type=click.Path(writable=True),
    default="merit_badges_image_trainer.apkg",
    help="Output file path",
)
@click.option("--deck-name", default="Merit Badges Visual Trainer", help="Anki deck name")
@click.option("--model-name", default="Merit Badge Image → Text", help="Anki model name")
@click.option("--dry-run", is_flag=True, default=False, help="Run without writing .apkg file")
@click.option("-q", "--quiet", is_flag=True, help="Only show errors")
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
def build(
    directory_path,
    out,
    deck_name,
    model_name,
    dry_run,
    quiet,
    verbose,
):
    """Build Anki deck from extracted directory."""

    # Setup logging
    logger = setup_logging(quiet=quiet, verbose=verbose)

    try:
        # Process directory
        logger.info(f"Processing directory: {directory_path}")
        badges, available_images = directory.process_directory(directory_path)

        if not badges:
            raise NoBadgesFoundError("No badges found in directory")

        if not available_images:
            raise ValueError("No images found in directory")

        # Map badges to images
        logger.info("Mapping badges to images...")
        mapped_badges, unmapped_badges = mapping.map_badges_to_images(badges, available_images)

        # Create mapping summary
        summary = mapping.create_mapping_summary(
            badges, available_images, mapped_badges, unmapped_badges
        )

        # Print summary
        print_build_summary(summary, dry_run)

        if not mapped_badges:
            logger.error("No badges could be mapped to images")
            sys.exit(4)

        # Build deck (unless dry run)
        if not dry_run:
            logger.info("Building Anki deck...")
            anki_deck, media_files = deck.create_merit_badge_deck(
                deck_name=deck_name,
                model_name=model_name,
                mapped_badges=mapped_badges,
                available_images=available_images,
            )

            # Write package
            logger.info(f"Writing package to {out}")
            deck.write_anki_package(anki_deck, media_files, out)

            # Cleanup temp files
            deck.cleanup_temp_files(media_files)

            logger.info(f"Successfully created {out}")
        else:
            logger.info("Dry run complete - no .apkg file written")

    except ValueError as e:
        if "No images found" in str(e):
            logger.error(str(e))
            sys.exit(3)
    except NoBadgesFoundError as e:
        logger.error(str(e))
        sys.exit(4)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def print_build_summary(summary: dict, dry_run: bool = False) -> None:
    """Print build summary table."""
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
