"""Command line interface for scout-anki."""

import sys

import click

from .adventure_processor import AdventureProcessor
from .config import create_sample_config, save_sample_config
from .errors import NoBadgesFoundError
from .log import setup_logging
from .merit_badge import MeritBadgeProcessor


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
        # Create appropriate processor
        if deck_type == "merit-badges":
            processor = MeritBadgeProcessor()
        elif deck_type == "cub-adventures":
            processor = AdventureProcessor()

        # Build deck using processor
        processor.build_deck(directory_path, out, deck_name, model_name, dry_run)

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


@cli.command()
@click.option("--show", is_flag=True, help="Show sample configuration")
@click.option("--save", type=click.Path(), help="Save sample configuration to file")
def config(show, save):
    """Manage configuration."""
    if show:
        click.echo("Sample configuration:")
        click.echo(create_sample_config())
    elif save:
        message = save_sample_config(save)
        click.echo(message)
    else:
        # Default: save to current directory
        message = save_sample_config()
        click.echo(message)
