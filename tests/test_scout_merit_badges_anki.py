"""Basic integration tests."""

import json
import tempfile
from pathlib import Path

from scout_anki.merit_badges.processor import MeritBadgeProcessor


def test_directory_processing():
    """Test processing a directory with badges and images."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)

        # Create test JSON file
        badges_data = [
            {"name": "Archery", "description": "Learn archery skills"},
            {"name": "Camping", "description": "Learn camping skills"},
        ]
        json_file = test_dir / "badges.json"
        json_file.write_text(json.dumps(badges_data))

        # Create test image files
        (test_dir / "archery.jpg").write_bytes(b"fake archery image")
        (test_dir / "camping.png").write_bytes(b"fake camping image")

        # Process directory
        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(test_dir)

        assert len(badges) == 2
        assert len(images) == 2
        assert "archery.jpg" in images
        assert "camping.png" in images


def test_empty_directory():
    """Test processing an empty directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        processor = MeritBadgeProcessor()
        badges, images = processor.process_directory(temp_dir)

        assert len(badges) == 0
        assert len(images) == 0
