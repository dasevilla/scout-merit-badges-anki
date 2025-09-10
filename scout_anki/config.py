"""Configuration system for scout-anki."""

import json
from pathlib import Path
from typing import Any

from .log import get_logger


class Config:
    """Configuration manager for scout-anki."""

    def __init__(self):
        self.logger = get_logger()
        self._config = {}
        self._load_config()

    def _get_config_paths(self) -> list[Path]:
        """Get list of config file paths to check."""
        paths = []

        # Current directory
        paths.append(Path.cwd() / "scout-anki.json")

        # Home directory
        home = Path.home()
        paths.append(home / ".scout-anki.json")
        paths.append(home / ".config" / "scout-anki" / "config.json")

        return paths

    def _load_config(self) -> None:
        """Load configuration from files."""
        for config_path in self._get_config_paths():
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        file_config = json.load(f)
                        self._config.update(file_config)
                        self.logger.debug(f"Loaded config from {config_path}")
                        break
                except (json.JSONDecodeError, OSError) as e:
                    self.logger.warning(f"Failed to load config from {config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def get_deck_config(self, deck_type: str) -> dict[str, Any]:
        """Get configuration for specific deck type."""
        deck_configs = self.get("decks", {})
        return deck_configs.get(deck_type, {})

    def get_deck_default(self, deck_type: str, key: str, fallback: Any = None) -> Any:
        """Get default value for deck type."""
        deck_config = self.get_deck_config(deck_type)
        return deck_config.get(key, fallback)


# Global config instance
_config = None


def get_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def create_sample_config() -> str:
    """Create sample configuration content."""
    sample = {
        "decks": {
            "merit-badges": {
                "out": "my_merit_badges.apkg",
                "deck_name": "My Merit Badge Collection",
                "model_name": "Merit Badge Quiz",
            },
            "cub-adventures": {
                "out": "my_cub_adventures.apkg",
                "deck_name": "My Cub Scout Adventures",
                "model_name": "Adventure Quiz",
            },
        },
        "logging": {"level": "INFO"},
    }
    return json.dumps(sample, indent=2)


def save_sample_config(path: str = "scout-anki.json") -> None:
    """Save sample configuration to file."""
    config_path = Path(path)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(create_sample_config())
    # Return message for CLI to print
    return f"Sample configuration saved to {config_path}"
