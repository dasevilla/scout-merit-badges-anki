"""Custom exception types for scout-merit-badges-anki."""


class ScoutAnkiError(Exception):
    """Base exception for scout-merit-badges-anki."""

    pass


class NoBadgesFoundError(ScoutAnkiError):
    """Parsing JSON yielded zero badges."""

    pass


class NoImagesFoundError(ScoutAnkiError):
    """No images found in directory."""

    pass


class ValidationError(ScoutAnkiError):
    """Validation failed with missing images."""

    pass
