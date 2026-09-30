# Cookie recipes

Opinionated Cookiecutter recipes for Python and Vue projects.
Python projects use [uv](https://docs.astral.sh/uv/); Vue projects use npm.

## FastAPI

```sh
uvx cookiecutter . --directory recipes/fastapi
```

The recipe includes FastAPI, uv, Ruff, ty, import-linter, HTTPX2, and Tortoise ORM.
It defaults to Python 3.13 and SQLite, with an example item API, smoke tests, and Docker Compose.
Choose `postgresql` for the `database` prompt to include the asyncpg driver, PostgreSQL
configuration, a PostgreSQL Compose service with persistent storage, and PostgreSQL CI tests.
Generated projects include GitHub CI and a tag-driven release workflow that publishes to GHCR.
Dependabot checks weekly for separate Python runtime, Python tooling, Docker image, and Actions
update groups. PostgreSQL projects also track the database image in Compose. Python version
updates have a seven-day cooldown.

Imports follow `api → services → db`, with shared Pydantic schemas in `domain`.
Import-linter prevents direct API/database imports, reverse dependencies, and framework
dependencies in the domain. The generated README contains setup and quality-check commands.

Recipe inputs are `project_name`, `project_slug`, `module_name`, `description`, and
`database` (`sqlite` or `postgresql`, with SQLite selected by default).
Names default from the project name; the hook rejects invalid slugs and Python module names.

## FastAPI + Vue

```sh
uvx cookiecutter . --directory recipes/fastapi-vue
```

This recipe reuses the FastAPI template and its SQLite/PostgreSQL choice, and adds a
TypeScript frontend in `frontend/`: Vite 8, Vue 3.6 RC, Vue Router 5, Vue I18n 12 alpha,
Pinia, Oxlint with e18e rules, Oxfmt, Knip, vue-tsc, and Vitest.
TypeScript stays on version 6. `frontend/README.md` documents the upgrades to stable Vue,
stable Vue I18n, and TypeScript 7 once Vue language tools support it.
Vue I18n 12 has no published RC as of 2026-09-30, so the latest version 12 alpha is used.

The e18e CLI supplies dependency replacement codemods. Frontend dependencies have a
committed npm lockfile and separate Dependabot runtime/tooling groups. CI runs frontend
formatting, linting, types, tests, dead-code checks, and a production build alongside the
backend gates. Compose adds an Nginx container serving the Vue build on port 8080 and
proxying API requests. Releases publish both backend and frontend images to GHCR.

The `backend` symlink points to the existing FastAPI recipe. Cookiecutter's pre-prompt
hook merges it into a temporary template copy before rendering the Vue overlay; backend
code and checks stay maintained in one place. Use Cookiecutter 2.7.1 or newer with hooks enabled.

## Vue

```sh
uvx cookiecutter . --directory recipes/vue
```

The standalone recipe includes the same frontend toolchain, versions, lockfile, codemods,
and upgrade TODOs as `fastapi-vue`. Its example stores items in memory with Pinia and
uses English/Spanish messages through Vue I18n. Inputs are `project_name`, `project_slug`,
and `description`. It includes a non-root Nginx Docker image, Compose, frontend CI checks,
grouped Dependabot, and a release workflow publishing to GHCR using `frontend/package.json`.

The shared frontend and Docker files live in `recipes/vue`; `fastapi-vue` references them
with symlinks. Cookiecutter's temporary template copy resolves the links before rendering.

## Check the recipe

```sh
uv run --no-project --with cookiecutter python -m unittest discover -s tests -v
```

This renders both FastAPI recipes with SQLite and PostgreSQL, plus default and renamed
standalone Vue projects, in temporary directories. It installs
their dependencies, runs the backend and frontend gates, and verifies that import contracts,
e18e rules, and Knip reject violations. It also checks that both recipes render the same backend.

Set `RUN_DOCKER_TESTS=1` on the same command to build all generated images and verify
database persistence across container replacement, SPA routing, and API proxying.
Tests require uv and Node 26.10.0 or newer; Docker checks also require Docker with Compose.
The other backend gates use SQLite to run without a server.

This repository's GitHub CI runs those checks for all recipes and database choices.
The repository's own Dependabot configuration tracks GitHub Actions and the Vue template's
valid npm manifest, lockfile, and Dockerfile. Generated projects also track Python dependencies
and all container images.
