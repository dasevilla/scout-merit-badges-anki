"""Tests for cub adventure functionality."""

import json
import tempfile
from pathlib import Path

from scout_anki.cub_adventures.processor import AdventureProcessor


def test_cub_adventure_directory_processing():
    """Test processing directory with cub adventure data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create rank directory structure
        tiger_dir = test_dir / "tiger"
        tiger_dir.mkdir()
        images_dir = tiger_dir / "images"
        images_dir.mkdir()

        # Create test adventure data with expected field names
        adventure_data = {
            "adventure_name": "Backyard Jungle",
            "rank_name": "Tiger",
            "adventure_type": "Adventure",
            "adventure_overview": "Explore nature",
            "image_filename": "jungle.png",
        }

        # Write JSON file in rank directory
        (tiger_dir / "backyard-jungle.json").write_text(json.dumps(adventure_data))

        # Create image file in images subdirectory
        (images_dir / "jungle.png").write_bytes(b"fake jungle image")

        # Process directory
        processor = AdventureProcessor()
        adventures, images = processor.process_directory(str(test_dir))

        assert len(adventures) == 1
        assert len(images) == 1
        assert adventures[0].name == "Backyard Jungle"
        assert "jungle.png" in images


def test_cub_adventure_empty_directory():
    """Test processing empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = AdventureProcessor()
        adventures, images = processor.process_directory(temp_dir)

        assert len(adventures) == 0
        assert len(images) == 0


def test_cub_adventure_defaults():
    """Test cub adventure processor defaults."""
    processor = AdventureProcessor()
    defaults = processor.get_defaults()

    assert defaults["out"] == "cub_scout_adventure_image_trainer.apkg"
    assert defaults["deck_name"] == "Cub Scout Adventure Image Trainer"
    assert defaults["model_name"] == "Cub Scout Adventure Quiz"


def test_cub_adventure_mapping():
    """Test cub adventure to image mapping."""
    processor = AdventureProcessor()

    # Mock adventure data
    from scout_anki.cub_adventures.schema import Adventure

    adventures = [
        Adventure(
            name="Backyard Jungle",
            rank="Tiger",
            type="Adventure",
            overview="Test",
            image_filename="jungle.png",
        )
    ]
    images = {"jungle.png": Path("jungle.png")}

    mapped, unmapped = processor.map_content_to_images(adventures, images)

    assert len(mapped) == 1
    assert len(unmapped) == 0
    assert mapped[0][0].name == "Backyard Jungle"
    assert mapped[0][1] == "jungle.png"
