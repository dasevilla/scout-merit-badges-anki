"""Configuration management for scout-merit-badges-anki."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    # Anki settings
    default_deck_name: str = "Merit Badges Image Trainer"
    default_model_name: str = "Merit Badge Image → Text"
    default_output_file: str = "merit_badges_image_trainer.apkg"

    # Image settings
    max_image_width: str = "85%"
    image_style: str = "max-width: 85%; height: auto;"

    # Logging settings
    log_format_simple: str = "%(levelname)s: %(message)s"
    log_format_verbose: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# Global config instance
config = Config()
