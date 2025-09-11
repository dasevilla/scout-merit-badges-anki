"""Tests for merit badge functionality."""

import json
import tempfile
from pathlib import Path

from scout_anki.merit_badges.processor import MeritBadgeProcessor


def test_merit_badge_directory_processing():
    """Test processing directory with merit badge data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create test badge data
        badge_data = [
            {
                "name": "Camping",
                "description": "Learn outdoor skills",
                "image_filename": "camping.png",
            },
            {"name": "Hiking", "description": "Trail adventures", "image_filename": "hiking.jpg"},
        ]

        # Write JSON file
        (test_dir / "badges.json").write_text(json.dumps(badge_data))

        # Create image files
        (test_dir / "camping.png").write_bytes(b"fake camping image")
        (test_dir / "hiking.jpg").write_bytes(b"fake hiking image")

        # Process directory
        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(str(test_dir))

        assert len(badges) == 2
        assert len(images) == 2
        assert badges[0].name == "Camping"
        assert "camping.png" in images


def test_merit_badge_empty_directory():
    """Test processing empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(temp_dir)

        assert len(badges) == 0
        assert len(images) == 0


def test_merit_badge_defaults():
    """Test merit badge processor defaults."""
    processor = MeritBadgeProcessor()
    defaults = processor.get_defaults()

    assert defaults["out"] == "merit_badges_image_trainer.apkg"
    assert defaults["deck_name"] == "Merit Badges Image Trainer"
    assert defaults["model_name"] == "Merit Badge Quiz"


def test_merit_badge_mapping():
    """Test merit badge to image mapping."""
    processor = MeritBadgeProcessor()

    # Mock badge data
    from scout_anki.merit_badges.schema import MeritBadge

    badges = [MeritBadge(name="Camping", description="Test", image_filename="camping.png")]
    images = {"camping.png": Path("camping.png")}

    mapped, unmapped = processor.map_content_to_images(badges, images)

    assert len(mapped) == 1
    assert len(unmapped) == 0
    assert mapped[0][0].name == "Camping"
    assert mapped[0][1] == "camping.png"
