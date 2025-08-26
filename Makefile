.PHONY: fmt lint test test-cov test-no-cov cov-report build-deck clean setup-pre-commit check-all help fetch-releases extract-archives fetch-and-build

help:
	@echo "Available commands:"
	@echo "  fetch-and-build  - Fetch, extract, and build deck in one command"
	@echo "  fetch-releases   - Fetch scout-archive releases using gh CLI"
	@echo "  extract-archives - Extract downloaded archives to extracted/ directory"
	@echo "  build-deck       - Build Anki deck from extracted directory"
	@echo "  setup-pre-commit - Install pre-commit hooks"
	@echo "  check-all        - Run all pre-commit hooks on all files"
	@echo "  fmt              - Format code with ruff"
	@echo "  lint             - Lint code with ruff"
	@echo "  test             - Run tests with coverage reporting (80% target)"
	@echo "  test-no-cov      - Run tests without coverage reporting"
	@echo "  cov-report       - Generate and open HTML coverage report"
	@echo "  clean            - Clean up temporary files"

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

build-deck:
	uv run scout-merit-badges-anki build extracted/

fetch-and-build: fetch-releases extract-archives build-deck

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
