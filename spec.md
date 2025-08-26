# Overview

Build a Python CLI tool, implemented with `click`, that generates an Anki `.apkg` deck of merit badges from the **latest** or a **given** GitHub release in the `scout-archive` repository. Cards show the badge image on the front, and on the back show the badge name and a brief description. Images in releases follow the pattern `american-business-merit-badge.jpg`. Source data is updated roughly weekly.

# Success Criteria

- Given a public GitHub release containing badge JSON and images, the command `scoutanki build` outputs a valid `.apkg` that can be imported into Anki with one note per badge, media bundled.
- Stable model and deck IDs are derived from deterministic hashes so repeated runs do not create duplicate models.
- If a tag is omitted, the latest release is used. If a tag is provided, that specific release is used. If a token is provided, the tool respects it for higher rate limits.
- The tool reports counts of parsed badges, attached images, skipped items, and the output path. Non zero exit on fatal errors.

# User Stories

- As a Scout leader, I run `scoutanki build` weekly to regenerate the deck from the newest release, then import into Anki for personal study or to share.
- As a contributor, I run `scoutanki validate --tag <T>` to confirm a given release has the expected JSON and images before publishing.

# CLI Design

## Commands

1. `scoutanki build`
   - Purpose, fetch release assets, parse JSON, map images, build `.apkg`.
   - Options,
     - `--repo TEXT`, default `dasevilla/scout-archive`.
     - `--tag TEXT`, optional release tag, for example `archive-YYYY-MM-DD-HHMM`.
     - `--token TEXT`, optional GitHub token, may also read `GITHUB_TOKEN`.
     - `--out PATH`, default `merit_badges_image_trainer.apkg`.
     - `--deck-name TEXT`, default `Merit Badges, Image Trainer`.
     - `--model-name TEXT`, default `Merit Badge Image → Text`.
     - `--reverse/--no-reverse`, add a Name to Image card, default disabled.
     - `--include-eagle-tags/--no-include-eagle-tags`, if JSON has `is_eagle_required`, tag notes with `eagle`, default enabled.
     - `--dry-run`, run everything except writing `.apkg`, print a summary table.
     - `-q, --quiet` and `-v, --verbose` logging controls.

2. `scoutanki validate`
   - Purpose, inspect a release, print counts, list missing images, and spot JSON issues without building the deck.
   - Same options for `--repo`, `--tag`, `--token`.
   - Exit code non zero on validation errors.

3. `scoutanki list-releases`
   - Purpose, list recent release tags and publish times to help the user choose.
   - Options, `--repo`, `--token`, `--limit INTEGER` default 10.

## Example usage

```bash
scoutanki build                       # latest release
scoutanki build --tag archive-2025-08-25-1426
scoutanki build --reverse --out badges.apkg
scoutanki validate --tag archive-2025-09-01-1415
scoutanki list-releases --limit 5
```

# Architecture

```
src/
  scoutanki/
    __init__.py
    cli.py             # click entrypoints
    github.py          # GitHub API calls for releases and asset downloads
    archive.py         # read zip, tar.gz, single files, iterate members
    schema.py          # Badge model and normalization
    mapping.py         # image selection by name pattern and explicit JSON
    deck.py            # genanki model, deck, and package creation
    log.py             # logger setup
    errors.py          # custom exception types
```

- `Badge` model fields, `name` (str), `description` (str), `image` (str, optional), `is_eagle_required` (bool, optional), `source` (str, optional).
- Deterministic IDs, `stable_id(seed: str) -> int` using `sha1(seed)[:10]` as hex to int.
- HTTP logic in `github.py` supports anonymous and token authenticated requests, sets a clear UA, retries on transient status codes.

# Data Assumptions and Normalization

## Release assets

- Assets may be zip, tar.gz, tar, or loose `.json` and image files.
- Badge images include names like `*-merit-badge.jpg`.
- JSON can be a list or a dict with a list under a key such as `badges`, `items`, `data`, or `meritBadges`.

## JSON schema normalization

Accept the following keys, case sensitive as typical JSON,

- Name, `name` or `title` or `badge`.
- Description, `overview` or `description` or `blurb` or `summary`.
- Image filename, `image` or `img` or `icon`.
- Eagle flag, `is_eagle_required` boolean.

Normalization rules,

- Trim whitespace of strings, drop records missing `name`.
- Keep the first occurrence for duplicates by name.

# Image Mapping Strategy

- If the JSON specifies an image filename, match by basename against the assets.
- Otherwise infer from `name` using slug rules, lower case, non alphanumeric replaced with dashes, then prefer `<slug>-merit-badge.*`.
- If multiple candidates match, choose the shortest basename.
- If no image is found, skip that badge and report it in the summary.

# Deck and Note Construction

- Model, fields, `[Image, Name, Description]`.
- Front template, `<img src="{{Image}}">` centered and constrained to 85 percent width.
- Back template, show FrontSide, then Name and Description.
- Optional reverse card, query `{{Name}}` on front, show image and description on back.
- Tags, include `eagle` when `is_eagle_required is true` if `--include-eagle-tags`.
- GUID, `genanki.guid_for(f"{slug(name)}|{image_basename}")`.
- Deck ID and Model ID derived from `stable_id(f"{repo}:{deck_name}")` and `stable_id(f"{repo}:{model_name}")`.

# Error Handling and Exit Codes

- Non zero exit when,
  - GitHub release not found, 2.
  - No JSON or no images found in assets, 3.
  - Parsing JSON yields zero badges, 4.
  - Network error unrecoverable, 5.
- Validation prints a compact table of badge names with missing images and returns 6 if any are missing.

# Logging

- Default is info level, verbose prints HTTP endpoints, counts per phase, and timing, quiet prints only final summary and errors.
- Colorized output is fine, avoid heavy dependencies.

# Implementation Details

## GitHub API

- Endpoints,
  - Latest release, `GET /repos/{owner}/{repo}/releases/latest`.
  - Specific tag, `GET /repos/{owner}/{repo}/releases/tags/{tag}`.
  - Asset download, use `browser_download_url`.
- Headers, `Accept: application/vnd.github+json`, optional `Authorization: Bearer <token>`.
- Retries, two short retries on `429, 502, 503, 504`.

## Archives

- Support `.zip`, `.tar.gz`, `.tgz`, `.tar`.
- Iterate members without extracting to disk, keep file path strings for name matching.
- Only write image files that are used into the working directory so they can be bundled in `genanki.Package.media_files`.

## Deterministic hashing

- `stable_id(seed)`, `int(sha1(seed.encode()).hexdigest()[:10], 16)`.
- `slug(s)`, lower case, spaces to dashes, remove non alphanumeric and hyphen.

# click Skeleton

```python
import click
from . import deck, github, archive, mapping, schema

@click.group()
def cli():
    """Scout Archive to Anki deck tools."""

@cli.command()
@click.option("--repo", default="dasevilla/scout-archive")
@click.option("--tag")
@click.option("--token", envvar="GITHUB_TOKEN")
@click.option("--out", type=click.Path(writable=True), default="merit_badges_image_trainer.apkg")
@click.option("--deck-name", default="Merit Badges, Image Trainer")
@click.option("--model-name", default="Merit Badge Image → Text")
@click.option("--reverse/--no-reverse", default=False)
@click.option("--include-eagle-tags/--no-include-eagle-tags", default=True)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("-q", "--quiet", is_flag=True)
@click.option("-v", "--verbose", count=True)
def build(repo, tag, token, out, deck_name, model_name, reverse, include_eagle_tags, dry_run, quiet, verbose):
    # 1) fetch release json
    # 2) download assets
    # 3) gather JSON and images
    # 4) normalize badges
    # 5) map images
    # 6) build deck, optionally add reverse template
    # 7) write .apkg unless dry run
    ...

@cli.command("validate")
@click.option("--repo", default="dasevilla/scout-archive")
@click.option("--tag")
@click.option("--token", envvar="GITHUB_TOKEN")
def validate_cmd(repo, tag, token):
    # fetch, download, parse, print findings, return non zero on problems
    ...

@cli.command("list-releases")
@click.option("--repo", default="dasevilla/scout-archive")
@click.option("--token", envvar="GITHUB_TOKEN")
@click.option("--limit", default=10)
def list_releases(repo, token, limit):
    ...
```

# Packaging and Tooling

## pyproject.toml

```toml
[project]
name = "scoutanki"
version = "0.1.0"
description = "Build Anki decks from scout-archive releases"
requires-python = ">=3.11"
dependencies = [
  "click>=8.1",
  "requests>=2.32",
  "genanki>=0.13.1",
]

[project.scripts]
scoutanki = "scoutanki.cli:cli"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E","F","I","UP","B","RUF"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## pre-commit

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format
```

## Makefile

```make
.PHONY: venv fmt lint test run

venv:
	uv venv && . .venv/bin/activate && uv pip install -e .

fmt:
	ruff format

lint:
	ruff check

test:
	pytest -q

run:
	scoutanki build
```

# Edge Cases and Rules

- If multiple JSON files exist, merge their badge lists then de duplicate by `name`.
- If images with the same basename exist in different folders, prefer the shortest path.
- If description is empty, still create the card using just Name.
- If there are zero usable badges after parsing, exit with a clear message and non zero code.
- If a user supplies `--reverse`, add an additional template to the model that produces a second card per note.

# Validation Output

- Counts, total badges in JSON, images available, notes created, skipped.
- Missing images list, badge names and expected inferred image basenames.
- Unknown image files, present in assets but not referenced by any badge after mapping, optional.

# Test Plan

- Unit tests for,
  - JSON normalization, assorted schema shapes, including empty fields.
  - Slug and image selection, including the `*-merit-badge` pattern.
  - Stable IDs remain stable across runs.
  - Archive readers for `.zip` and `.tar.gz`.
- Integration tests,
  - Use a small synthetic release archive with three badges and images to assert note count and media bundling.
  - Dry run path produces summary without `.apkg` file.
- Smoke test,
  - Hit the real GitHub release, guarded by an env var and skipped in CI by default.

# Performance and Limits

- Badges count is low, memory footprint is tiny. Stream assets in memory, avoid writing everything to disk. Only write images that are included.
- GitHub anonymous rate limit is low, recommend passing a token if frequent runs are expected.

# Security and Privacy

- The tool only reads public release assets. If a token is provided, do not log it. Redact tokens from any error messages.

# Handover Notes for the Implementing LLM

- Follow the module boundaries exactly to keep the code clear.
- Keep the JSON normalization logic in one place so schema changes are easy.
- Prefer small focused functions with type hints.
- Write concise docstrings and keep logging human readable.
- Start by implementing `list-releases`, then `validate`, then `build`.
- After implementation, generate a minimal `--help` output and confirm all options are documented.
