# Cookie recipes

Opinionated Cookiecutter recipes for Python projects, managed with [uv](https://docs.astral.sh/uv/).

## FastAPI

```sh
uvx cookiecutter . --directory recipes/fastapi
```

The recipe includes FastAPI, uv, Ruff, ty, import-linter, HTTPX2, and Tortoise ORM.
It defaults to Python 3.13 and SQLite, with an example item API, smoke tests, and Docker Compose.
Generated projects include GitHub CI and a tag-driven release workflow that publishes to GHCR.

Imports follow `api → services → db`, with shared Pydantic schemas in `domain`.
Import-linter prevents direct API/database imports, reverse dependencies, and framework
dependencies in the domain. The generated README contains setup and quality-check commands.

Recipe inputs are `project_name`, `project_slug`, `module_name`, and `description`.
Names default from the project name; the hook rejects invalid slugs and Python module names.

## Check the recipe

```sh
uv run --no-project --with cookiecutter python -m unittest discover -s tests -v
```

This renders the default recipe and a renamed project in temporary directories, installs their
dependencies with uv, runs formatting, linting, typing, and API checks, and verifies that import
contracts reject forbidden dependencies.

Set `RUN_DOCKER_TESTS=1` on the same command to also build both generated projects' images
and check SQLite persistence across container replacement. This requires Docker with Compose.

This repository's GitHub CI runs those checks for both the default and renamed project.
