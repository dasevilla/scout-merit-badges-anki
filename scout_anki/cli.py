"""Command line interface for scout-merit-badges-anki."""

import sys

import click

from . import adventure, deck, directory, mapping
from .errors import (
    NoBadgesFoundError,
)
from .log import setup_logging


@click.group()
def cli():
    """Scout Archive to Anki deck tools."""
    pass


@cli.command()
@click.argument("deck_type", type=click.Choice(["merit-badges", "cub-adventures"]))
@click.argument("directory_path", type=click.Path(exists=True, file_okay=False, readable=True))
@click.option(
    "--out",
    type=click.Path(writable=True),
    help="Output file path (default: auto-generated based on deck type)",
)
@click.option("--deck-name", help="Anki deck name (default: auto-generated based on deck type)")
@click.option("--model-name", help="Anki model name (default: auto-generated based on deck type)")
@click.option("--dry-run", is_flag=True, default=False, help="Run without writing .apkg file")
@click.option("-q", "--quiet", is_flag=True, help="Only show errors")
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
def build(
    deck_type,
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
        if deck_type == "merit-badges":
            build_merit_badge_deck(directory_path, out, deck_name, model_name, dry_run, logger)
        elif deck_type == "cub-adventures":
            build_cub_adventure_deck(directory_path, out, deck_name, model_name, dry_run, logger)

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


def build_merit_badge_deck(directory_path, out, deck_name, model_name, dry_run, logger):
    """Build merit badge deck (existing functionality)."""
    # Set defaults for merit badges
    if not out:
        out = "merit_badges_image_trainer.apkg"
    if not deck_name:
        deck_name = "Merit Badges Visual Trainer"
    if not model_name:
        model_name = "Merit Badge Image → Text"

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


def build_cub_adventure_deck(directory_path, out, deck_name, model_name, dry_run, logger):
    """Build Cub Scout adventure deck."""
    # Set defaults for adventures
    if not out:
        out = "cub_adventures_image_trainer.apkg"
    if not deck_name:
        deck_name = "Cub Scout Adventures"
    if not model_name:
        model_name = "Cub Scout Adventure Image → Text"

    # Process directory
    logger.info(f"Processing directory: {directory_path}")
    adventures, available_images = adventure.process_adventure_directory(directory_path)

    if not adventures:
        raise NoBadgesFoundError("No adventures found in directory")

    if not available_images:
        raise ValueError("No images found in directory")

    # Map adventures to images
    logger.info("Mapping adventures to images...")
    mapped_adventures, unmapped_adventures = adventure.map_adventures_to_images(
        adventures, available_images
    )

    # Create mapping summary
    summary = adventure.create_adventure_mapping_summary(
        adventures, available_images, mapped_adventures, unmapped_adventures
    )

    # Print summary
    print_adventure_summary(summary, dry_run)

    if not mapped_adventures:
        logger.error("No adventures could be mapped to images")
        sys.exit(4)

    # Build deck (unless dry run)
    if not dry_run:
        logger.info("Building Anki deck...")
        anki_deck, media_files = deck.create_adventure_deck(
            deck_name=deck_name,
            model_name=model_name,
            mapped_adventures=mapped_adventures,
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


def print_build_summary(summary: dict, dry_run: bool = False) -> None:
    """Print merit badge build summary table."""
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


def print_adventure_summary(summary: dict, dry_run: bool = False) -> None:
    """Print adventure build summary table."""
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
