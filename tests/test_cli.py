"""Tests for CLI functionality."""

import tempfile
from unittest.mock import Mock, patch

from click.testing import CliRunner

from scout_anki.cli import build, cli


class TestCLI:
    """Test CLI commands."""

    def test_cli_help(self):
        """Test main CLI help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Scout Archive to Anki deck tools" in result.output

    def test_build_help(self):
        """Test build command help."""
        runner = CliRunner()
        result = runner.invoke(build, ["--help"])
        assert result.exit_code == 0
        assert "Build Anki deck from extracted directory" in result.output
        assert "merit-badges" in result.output
        assert "cub-adventures" in result.output

    def test_build_missing_directory(self):
        """Test build command with missing directory."""
        runner = CliRunner()
        result = runner.invoke(build, ["merit-badges", "nonexistent"])
        assert result.exit_code != 0

    def test_build_dry_run_missing_directory(self):
        """Test build command dry run with missing directory."""
        runner = CliRunner()
        result = runner.invoke(build, ["merit-badges", "nonexistent", "--dry-run"])
        assert result.exit_code != 0


def test_build_merit_badges_success():
    """Test successful merit badge build."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "scout_anki.merit_badges.processor.MeritBadgeProcessor.process_directory"
        ) as mock_process:
            with patch(
                "scout_anki.merit_badges.processor.MeritBadgeProcessor.map_content_to_images"
            ) as mock_map:
                with patch("scout_anki.deck.create_merit_badge_deck") as mock_deck:
                    # Setup mocks
                    mock_process.return_value = (["badge"], {"test.jpg": "path"})
                    mock_map.return_value = ([("badge", "test.jpg")], [])
                    mock_deck.return_value = (Mock(), [])

                    runner = CliRunner()
                    result = runner.invoke(build, ["merit-badges", temp_dir, "--dry-run"])

                    assert result.exit_code == 0


def test_build_cub_adventures_success():
    """Test successful cub adventure build."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "scout_anki.cub_adventures.processor.AdventureProcessor.process_directory"
        ) as mock_process:
            with patch(
                "scout_anki.cub_adventures.processor.AdventureProcessor.map_content_to_images"
            ) as mock_map:
                with patch("scout_anki.deck.create_adventure_deck") as mock_deck:
                    # Setup mocks
                    mock_process.return_value = (["adventure"], {"test.jpg": "path"})
                    mock_map.return_value = ([("adventure", "test.jpg")], [])
                    mock_deck.return_value = (Mock(), [])

                    runner = CliRunner()
                    result = runner.invoke(build, ["cub-adventures", temp_dir, "--dry-run"])

                    assert result.exit_code == 0


def test_build_no_content_found():
    """Test build command when no content is found."""
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch(
            "scout_anki.merit_badges.processor.MeritBadgeProcessor.process_directory"
        ) as mock_process:
            mock_process.return_value = ([], {})

            runner = CliRunner()
            result = runner.invoke(build, ["merit-badges", temp_dir])

            assert result.exit_code == 4  # NoBadgesFoundError exit code
