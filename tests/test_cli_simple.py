"""Simple CLI tests."""

from click.testing import CliRunner

from scout_anki.cli import build, cli


class TestCLIBasic:
    """Basic CLI functionality tests."""

    def test_cli_help(self):
        """Test CLI help command."""
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
