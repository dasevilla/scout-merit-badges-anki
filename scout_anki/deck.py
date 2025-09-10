"""Anki deck and note creation using genanki."""

import os
import tempfile
from pathlib import Path

import genanki

from .log import get_logger
from .schema import Badge, slug, stable_id


def create_merit_badge_model(model_name: str) -> genanki.Model:
    """Create the Anki model for merit badge cards.

    Args:
        model_name: Name of the model

    Returns:
        Configured genanki Model
    """
    model_id = stable_id(model_name)

    # Base fields
    fields = [
        {"name": "Image"},
        {"name": "Name"},
        {"name": "Description"},
        {"name": "EagleRequired"},
    ]

    # Front template (Image → Name + Description)
    front_template = """
<div style="text-align: center;">
    {{Image}}
</div>
"""

    back_template = """
{{FrontSide}}
<hr>
<div style="text-align: center;">
    <h2>{{Name}} {{#EagleRequired}}<span class="eagle-badge">🦅</span>{{/EagleRequired}}</h2>
    <p>{{Description}}</p>
</div>
"""

    templates = [
        {
            "name": "Image → Name + Description",
            "qfmt": front_template,
            "afmt": back_template,
        }
    ]

    # CSS styling
    css = """
    .card {
        font-family: Arial, sans-serif;
        font-size: 16px;
        text-align: center;
        color: black;
        background-color: white;
    }

    h2 {
        color: #2c5aa0;
        margin: 10px 0;
    }

    p {
        margin: 10px 20px;
        line-height: 1.4;
    }

    img {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    hr {
        border: none;
        border-top: 1px solid #ccc;
        margin: 15px 0;
    }

    .eagle-badge {
        color: #b8860b;
        font-size: 0.9em;
        margin-left: 5px;
    }
    """

    return genanki.Model(
        model_id=model_id, name=model_name, fields=fields, templates=templates, css=css
    )


def create_merit_badge_note(badge: Badge, image_name: str, model: genanki.Model) -> genanki.Note:
    """Create an Anki note for a merit badge.

    Args:
        badge: Badge data
        image_name: Name of the image file
        model: Anki model to use

    Returns:
        Configured genanki Note
    """
    # Create GUID from badge name and image
    badge_slug = slug(badge.name)
    image_basename = os.path.basename(image_name)
    guid = genanki.guid_for(f"{badge_slug}|{image_basename}")

    # Prepare fields - put complete img tag with styling in the field
    fields = [
        f'<img src="{image_name}" style="max-width: 85%; height: auto;">',  # Image with styling
        badge.name,  # Name
        badge.description or "",  # Description
        "1" if badge.eagle_required else "",  # EagleRequired (non-empty for true)
    ]

    return genanki.Note(model=model, fields=fields, guid=guid)


def create_merit_badge_deck(
    deck_name: str,
    model_name: str,
    mapped_badges: list[tuple[Badge, str]],
    available_images: dict[str, Path],
) -> tuple[genanki.Deck, list[str]]:
    """Create an Anki deck with merit badge notes.

    Args:
        deck_name: Name of the deck
        model_name: Name of the model
        mapped_badges: List of (badge, image_name) tuples
        available_images: Dict mapping image names to file paths

    Returns:
        Tuple of (deck, list of media file paths)
    """
    logger = get_logger()

    # Create model
    model = create_merit_badge_model(model_name)

    # Create deck
    deck_id = stable_id(deck_name)
    deck = genanki.Deck(deck_id=deck_id, name=deck_name)

    # Create temporary directory for media files
    temp_dir = tempfile.mkdtemp(prefix="scout_anki_")
    media_files = []

    # Create notes
    for badge, image_name in mapped_badges:
        # Copy image file to temp directory
        source_path = available_images[image_name]
        image_path = os.path.join(temp_dir, image_name)

        import shutil

        shutil.copy2(source_path, image_path)
        media_files.append(image_path)

        # Create note
        note = create_merit_badge_note(badge=badge, image_name=image_name, model=model)
        deck.add_note(note)

    logger.info(f"Created deck '{deck_name}' with {len(mapped_badges)} notes")

    return deck, media_files


def write_anki_package(deck: genanki.Deck, media_files: list[str], output_path: str) -> None:
    """Write Anki package to file.

    Args:
        deck: Anki deck to write
        media_files: List of media file paths
        output_path: Output file path
    """
    logger = get_logger()

    # Create package
    package = genanki.Package(deck)
    package.media_files = media_files

    # Write to file
    package.write_to_file(output_path)

    logger.info(f"Wrote Anki package to: {output_path}")


def cleanup_temp_files(media_files: list[str]) -> None:
    """Clean up temporary media files.

    Args:
        media_files: List of temporary file paths to clean up
    """
    logger = get_logger()

    for file_path in media_files:
        try:
            os.unlink(file_path)
        except OSError as e:
            logger.warning(f"Failed to clean up temp file {file_path}: {e}")

    # Try to remove temp directory if empty
    if media_files:
        temp_dir = os.path.dirname(media_files[0])
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass  # Directory not empty or other error, ignore
