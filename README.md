# scout-anki

Anki deck builder for Scouting content. Generates Anki decks for learning Scouting America merit badges and Cub Scout adventures by sight. The front of the card is an image of the merit badge or adventure loop. The back of the card is the name, description, and additional details.

## Usage

### Basic Usage

First, download and extract the scout-archive release files:

```bash
# Download and extract latest release archives for merit badges
make fetch-and-build-merit-badges

# Download and extract latest release archives for cub adventures
make fetch-and-build-cub-adventures

# Build both deck types
make fetch-releases extract-archives build-all
```

This downloads archives, extracts them to `extracted/` directory, and creates `.apkg` files that can be imported into Anki.

### Manual Usage

```bash
# Download archives
gh release download --repo dasevilla/scout-archive --pattern "*.tar.gz"

# Extract archives
mkdir -p extracted/
for file in *.tar.gz; do tar -xzf "$file" -C extracted/; done

# Generate merit badge Anki deck from extracted directory
scout-anki build merit-badges extracted/

# Generate cub adventure Anki deck from extracted directory
scout-anki build cub-adventures extracted/
```

### Advanced Usage

```bash
# Merit badges with custom output file
scout-anki build merit-badges extracted/ --out my_badges.apkg

# Cub adventures with custom output file
scout-anki build cub-adventures extracted/ --out my_adventures.apkg

# Dry run to preview without creating file
scout-anki build merit-badges extracted/ --dry-run
scout-anki build cub-adventures extracted/ --dry-run

# Custom deck and model names
scout-anki build merit-badges extracted/ --deck-name "My Badges" --model-name "Badge Quiz"
scout-anki build cub-adventures extracted/ --deck-name "My Adventures" --model-name "Adventure Quiz"
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

1. **Reads local archive files** (.tar.gz) containing Scouting data and images
2. **Extracts content data** from JSON files using flexible schema normalization
3. **Maps content to images** using direct `image_filename` field mapping
4. **Creates Anki deck** with stable IDs to prevent duplicates on reimport
5. **Bundles media files** into a complete .apkg package

### Image Mapping Strategy

The tool uses direct field mapping for reliable image association:

1. **Direct mapping**: Uses the `image_filename` field from JSON data
2. **100% success rate**: All badges and adventures now have explicit image filenames
3. **No pattern matching needed**: Simplified from complex inference logic

### Card Format

**Merit Badges:**
- **Front**: Merit badge image (centered, 85% width)
- **Back**: Badge name, description, and Eagle required indicator

**Cub Adventures:**
- **Front**: Adventure loop image (centered, 85% width)
- **Back**: Adventure name, rank, type, and description

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

## Data Source

This tool is built using data from the [scout-archive](https://github.com/dasevilla/scout-archive) repository, which is updated roughly weekly.
