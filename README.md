# scout-anki

Anki deck builder for Scouting content. Generates Anki decks for learning Scouting America merit badges by sight. The front of the card is an image of the merit badge. The back of the card is the name, description, and an indicator if it is required for the Eagle rank.

## Usage

### Basic Usage

First, download and extract the scout-archive release files:

```bash
# Download and extract latest release archives
make fetch-and-build
```

This downloads archives, extracts them to `extracted/` directory, and creates `merit_badges_image_trainer.apkg` that can be imported into Anki.

### Manual Usage

```bash
# Download archives
gh release download --repo dasevilla/scout-archive --pattern "*.zip" --pattern "*.tar.gz"

# Extract archives
mkdir -p extracted/
for file in *.zip; do unzip -q "$file" -d extracted/; done
for file in *.tar.gz; do tar -xzf "$file" -C extracted/; done

# Generate merit badge Anki deck from extracted directory
scout-anki build merit-badges extracted/
```

### Advanced Usage

```bash
# Merit badges with custom output file
scout-anki build merit-badges extracted/ --out my_badges.apkg

# Dry run to preview without creating file
scout-anki build merit-badges extracted/ --dry-run

# Cub Scout adventures (coming soon)
scout-anki build cub-adventures extracted/

# Custom deck and model names
scout-anki build merit-badges extracted/ --deck-name "My Badges" --model-name "Badge Quiz"
```

### Command Reference

#### `build` - Generate Anki deck

```bash
scout-anki build DECK_TYPE DIRECTORY [OPTIONS]
```

**Arguments:**
- `DECK_TYPE` - Type of deck to build: `merit-badges` or `cub-adventures`
- `DIRECTORY` - Directory containing extracted badge data and images

**Options:**
- `--out PATH` - Output file path (auto-generated based on deck type if not specified)
- `--deck-name TEXT` - Anki deck name (auto-generated based on deck type if not specified)
- `--model-name TEXT` - Anki model name (auto-generated based on deck type if not specified)
- `--dry-run` - Preview without creating .apkg file
- `-q, --quiet` - Only show errors
- `-v, --verbose` - Increase verbosity

## How It Works

1. **Reads local archive files** (.zip, .tar.gz) containing Scouting data and images
2. **Extracts content data** from JSON files using flexible schema normalization
3. **Maps content to images** using explicit filenames or smart pattern matching
4. **Creates Anki deck** with stable IDs to prevent duplicates on reimport
5. **Bundles media files** into a complete .apkg package

### Image Mapping Strategy

The tool uses a sophisticated strategy to match content with images:

1. **Explicit mapping**: If JSON specifies an image filename, match by basename
2. **Pattern matching**: Look for `<badge-slug>-merit-badge.*` format
3. **Exact slug match**: Match badge slug directly to image filename
4. **Shortest path preference**: When multiple candidates exist, choose the shortest filename

### Card Format

- **Front**: Merit badge image (centered, 85% width)
- **Back**: Badge name and description

## Development

To contribute to this tool, first checkout the code. Then set up the development environment:

```bash
cd scout-anki
uv sync
```

This will create a virtual environment and install all dependencies including development tools.

To set up pre-commit hooks (recommended):

```bash
make setup-pre-commit
```

To run the tests:

```bash
make test
```

### Development Commands

```bash
make setup-pre-commit # Install pre-commit hooks (REQUIRED)
make fmt              # Format code with ruff and fix linting issues
make lint             # Lint code with ruff (check only, no fixes)
make check-all        # Run all pre-commit hooks on all files
make test             # Run tests (8 focused tests)
make test-no-cov      # Run tests without coverage (faster for development)
make fetch-releases   # Download scout-archive releases using gh CLI
make extract-archives # Extract downloaded archives to extracted/ directory
make build-deck       # Build Anki deck from extracted directory
make fetch-and-build  # Fetch, extract, and build deck in one command
make clean            # Clean temporary files
```

## Data Source

This tool works with releases from the [scout-archive](https://github.com/dasevilla/scout-archive) repository, which contains merit badge data and images updated roughly weekly.
