# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install --with=dev,test

# Run all checks (lint + tests) — mirrors CI
poetry run tox

# Lint and type-check only
poetry run tox -e lint

# Tests with coverage only
poetry run tox -e py311

# Run a single test file or test
poetry run pytest tests/test_mermaid_controller.py -v
poetry run pytest tests/test_mermaid_controller.py::test_convert_success -v

# Formatting and linting separately
poetry run ruff format
poetry run ruff check
poetry run mypy .

# Build and run the container locally
docker build --build-arg APP_IMAGE_VERSION=0.0.0 -f Dockerfile -t mermaid-service:dev .
docker-compose up -d
```

Coverage must remain ≥ 80%. The `py311` tox environment enforces this automatically.

## Architecture

This is a thin FastAPI wrapper around the [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) (`mmdc`). The service accepts Mermaid diagram syntax and returns rendered SVG.

**Request flow:**
1. `POST /convert` or `POST /convert-with-styling` receives diagram text
2. `convert_mmd_to_svg()` in `mermaid_controller.py` writes the input to temp files, invokes `mmdc` via `subprocess.run`, reads the output `.svg`, then cleans up
3. The `mmdc` binary path comes from the `MMDC` env var (set by `entrypoint.sh` inside the container)
4. Puppeteer config at `/puppeteer-config.json` (from the base image) is always passed to `mmdc`

**Key files:**
- `app/mermaid_controller.py` — FastAPI app, all endpoints, subprocess invocation
- `app/mermaid_service_application.py` — entry point, CLI args (port, log level), uvicorn startup
- `app/schemas.py` — `VersionSchema` Pydantic model for `GET /version`
- `entrypoint.sh` — sets `MMDC`, `MERMAID_CLI_VERSION`, `MERMAID_SERVICE_BUILD_TIMESTAMP` before starting the app

**Endpoints:**
- `GET /version` — returns Python, Mermaid CLI, service version, and build timestamp
- `POST /convert` — plain-text body → SVG
- `POST /convert-with-styling` — multipart form with `mmd` (required) and `css` (optional) fields → SVG
- `GET /api/docs` — Swagger UI; OpenAPI spec served from `app/static/openapi.json`

## Conventions

**Dependencies:** Managed by Poetry. Dependencies are declared in `[tool.poetry.dependencies]` (not `[project.dependencies]`) due to a Renovate compatibility issue tracked in `pyproject.toml`. Do not migrate until that issue is resolved.

**Linting:** Ruff with a broad rule set (see `pyproject.toml`). Line length is 240. Tests are excluded from linting rules; `S101`, `PLR2004`, `F403`, `F405` are additionally ignored in test files. MyPy runs in strict mode on `app/` only.

**Commits:** Must follow [Conventional Commits](https://www.conventionalcommits.org/) — enforced by Commitizen in CI and pre-commit hooks. This drives automated semantic versioning via Release Please.

**Container base:** `minlag/mermaid-cli:11.12.0` (Alpine Linux). The service runs as non-root user `mermaidcli`. Logs go to `/opt/mermaid/logs/`.

**Test types:**
- Unit: `tests/test_mermaid_controller.py`, `test_schemas.py`, `test_logging.py`, `test_mermaid_service_application.py` — use the mock `mmdc` script at `tests/scripts/test_mmdc.sh`
- Integration: `tests/test_container.py` — requires Docker, spins up the built image using the Docker SDK

**Running the service locally** (without Docker; actual diagram conversion requires `mmdc` in PATH or `MMDC` env var set):
```bash
uv run python -m app.mermaid_service_application --port 9084
# or
uv run uvicorn app.mermaid_controller:app --host 127.0.0.1 --port 9084
```

## Code Review Guidelines

**Focus on:** subprocess invocation with user-provided input, temp file cleanup in `finally` blocks, `MMDC` env var handling, breaking API changes.

**Skip** (handled by automated tools):
- Formatting, imports, line length — Ruff
- Type annotations — MyPy
- Test coverage — Pytest + Coverage
