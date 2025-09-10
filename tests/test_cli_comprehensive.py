"""Basic CLI tests."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner

from scout_anki.cli import build


def test_build_with_valid_directory():
    """Test build command with valid directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("scout_anki.directory.process_directory") as mock_process:
            with patch("scout_anki.mapping.map_badges_to_images") as mock_map:
                with patch("scout_anki.deck.create_merit_badge_deck") as mock_deck:
                    # Setup mocks
                    mock_process.return_value = (["badge"], {"test.jpg": Path("test.jpg")})
                    mock_map.return_value = ([("badge", "test.jpg")], [])
                    mock_deck.return_value = (Mock(), [])

                    runner = CliRunner()
                    result = runner.invoke(build, [temp_dir, "--dry-run"])

                    assert result.exit_code == 0


def test_build_no_badges_found():
    """Test build command when no badges are found."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("scout_anki.directory.process_directory") as mock_process:
            mock_process.return_value = ([], {})

            runner = CliRunner()
            result = runner.invoke(build, [temp_dir])

            assert result.exit_code == 4  # NoBadgesFoundError exit code
