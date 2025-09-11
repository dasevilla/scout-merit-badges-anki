.PHONY: fmt lint test test-cov test-no-cov cov-report build-merit-badges build-cub-adventures build-all clean setup-pre-commit check-all help fetch-releases extract-archives fetch-and-build-merit-badges fetch-and-build-cub-adventures

help:
	@echo "Available commands:"
	@echo "  fetch-and-build-merit-badges     - Fetch, extract, and build merit badge deck"
	@echo "  fetch-and-build-cub-adventures   - Fetch, extract, and build cub adventure deck"
	@echo "  fetch-releases                   - Fetch scout-archive releases using gh CLI"
	@echo "  extract-archives                 - Extract downloaded archives to extracted/ directory"
	@echo "  build-merit-badges               - Build merit badge Anki deck from extracted directory"
	@echo "  build-cub-adventures             - Build cub adventure Anki deck from extracted directory"
	@echo "  build-all                        - Build both merit badge and cub adventure decks"
	@echo "  setup-pre-commit                 - Install pre-commit hooks"
	@echo "  check-all                        - Run all pre-commit hooks on all files"
	@echo "  fmt                              - Format code with ruff"
	@echo "  lint                             - Lint code with ruff"
	@echo "  test                             - Run tests with coverage reporting (80% target)"
	@echo "  test-no-cov                      - Run tests without coverage reporting"
	@echo "  cov-report                       - Generate and open HTML coverage report"
	@echo "  clean                            - Clean up temporary files"

setup-pre-commit:
	uv run pre-commit install
	@echo "Pre-commit hooks installed"

fmt:
	uv run ruff check --fix
	uv run ruff format

lint:
	uv run ruff check

check-all:
	uv run pre-commit run --all-files

test:
	uv run pytest

test-no-cov:
	uv run pytest --no-cov

cov-report:
	uv run pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/"

fetch-releases:
	gh release download --repo dasevilla/scout-archive --pattern "*.tar.gz"

extract-archives:
	mkdir -p extracted/
	for file in *.tar.gz; do [ -f "$$file" ] && tar -xzf "$$file" -C extracted/ || true; done

build-merit-badges:
	uv run scout-anki build merit-badges extracted/

build-cub-adventures:
	uv run scout-anki build cub-adventures extracted/

build-all: build-merit-badges build-cub-adventures

fetch-and-build-merit-badges: fetch-releases extract-archives build-merit-badges

fetch-and-build-cub-adventures: fetch-releases extract-archives build-cub-adventures

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .venv/
	rm -rf htmlcov/
	rm -rf extracted/
	rm -f .coverage
	rm -f coverage.xml
	rm -rf .*_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f *.apkg
	rm -f *.tar.gz
