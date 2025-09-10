"""Shared processing logic for different deck types."""

import sys
from abc import ABC, abstractmethod
from typing import Any

from . import deck
from .errors import NoBadgesFoundError, NoImagesFoundError
from .log import get_logger


class DeckProcessor(ABC):
    """Base class for deck processors."""

    def __init__(self, deck_type: str):
        self.deck_type = deck_type
        self.logger = get_logger()

    @abstractmethod
    def get_defaults(self) -> dict[str, str]:
        """Get default values for output, deck name, and model name."""
        pass

    @abstractmethod
    def process_directory(self, directory_path: str) -> tuple[list[Any], dict[str, Any]]:
        """Process directory and return content and images."""
        pass

    @abstractmethod
    def map_content_to_images(
        self, content: list[Any], images: dict[str, Any]
    ) -> tuple[list[tuple[Any, str]], list[Any]]:
        """Map content to images."""
        pass

    @abstractmethod
    def create_mapping_summary(
        self,
        content: list[Any],
        images: dict[str, Any],
        mapped: list[tuple[Any, str]],
        unmapped: list[Any],
    ) -> dict[str, Any]:
        """Create mapping summary."""
        pass

    @abstractmethod
    def print_summary(self, summary: dict[str, Any], dry_run: bool) -> None:
        """Print build summary."""
        pass

    @abstractmethod
    def create_deck(
        self,
        deck_name: str,
        model_name: str,
        mapped_content: list[tuple[Any, str]],
        images: dict[str, Any],
    ) -> tuple[Any, list[str]]:
        """Create Anki deck."""
        pass

    def build_deck(
        self,
        directory_path: str,
        out: str | None = None,
        deck_name: str | None = None,
        model_name: str | None = None,
        dry_run: bool = False,
    ) -> None:
        """Build deck with shared logic."""
        # Set defaults
        defaults = self.get_defaults()
        if not out:
            out = defaults["out"]
        if not deck_name:
            deck_name = defaults["deck_name"]
        if not model_name:
            model_name = defaults["model_name"]

        # Process directory
        self.logger.info(f"Processing directory: {directory_path}")
        content, available_images = self.process_directory(directory_path)

        if not content:
            raise NoBadgesFoundError(f"No {self.deck_type} found in directory")

        if not available_images:
            raise NoImagesFoundError("No images found in directory")

        # Map content to images
        self.logger.info(f"Mapping {self.deck_type} to images...")
        mapped_content, unmapped_content = self.map_content_to_images(content, available_images)

        # Create mapping summary
        summary = self.create_mapping_summary(
            content, available_images, mapped_content, unmapped_content
        )

        # Print summary
        self.print_summary(summary, dry_run)

        if not mapped_content:
            self.logger.error(f"No {self.deck_type} could be mapped to images")
            sys.exit(4)

        # Build deck (unless dry run)
        if not dry_run:
            self.logger.info("Building Anki deck...")
            anki_deck, media_files = self.create_deck(
                deck_name, model_name, mapped_content, available_images
            )

            # Write package
            self.logger.info(f"Writing package to {out}")
            deck.write_anki_package(anki_deck, media_files, out)

            # Cleanup temp files
            deck.cleanup_temp_files(media_files)

            self.logger.info(f"Successfully created {out}")
        else:
            self.logger.info("Dry run complete - no .apkg file written")
