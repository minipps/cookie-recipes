# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Run

```sh
uv sync
uv run tortoise init
uv run tortoise makemigrations --name initial
uv run tortoise migrate
uv run uvicorn {{ cookiecutter.module_name }}.main:create_app --factory --reload
```

Open http://127.0.0.1:8000/docs. `GET /health` checks that the process is serving.
`POST /api/v1/items` accepts `{"name": "Example"}`; `GET /api/v1/items/1` reads it back.
These example routes are unauthenticated; replace them with your application's endpoints.

SQLite is stored in `db.sqlite3` by default. Set `DATABASE_URL` to override the connection URL
for both the API and migration commands. Environment variables are read directly; `.env` files
are not loaded automatically. For PostgreSQL, install the driver with
`uv add 'tortoise-orm[asyncpg]'` and use a `postgres://` URL.

Commit `uv.lock` after `uv sync` and commit generated migrations. After editing models:

```sh
uv run tortoise makemigrations --name describe_change
uv run tortoise migrate
```

Apply migrations before starting the API. Startup opens connections without creating or
changing tables. The test creates a disposable schema in an in-memory database.

## Quality checks

```sh
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run lint-imports
uv run python -m unittest discover -s tests -v
```

Use `uv run ruff format .` and `uv run ruff check --fix .` to apply formatting and safe lint fixes.

## Architecture

```text
src/{{ cookiecutter.module_name }}/
  main.py         # composition root: FastAPI, routers, ORM lifespan
  api/            # HTTP routes; calls services, never imports storage directly
  services/       # application operations; calls storage, returns domain schemas
  db/             # Tortoise models, configuration, generated migrations
  domain/         # shared Pydantic schemas; no application or I/O imports
tests/            # HTTPX2 ASGI smoke test, no network or extra test framework
```

Import-linter allows API → services → DB while rejecting direct API → DB imports and
reverse dependencies. Type-checking imports are checked too. Application layers cannot
import `main`, which wires them together.

HTTPX2 is installed for outbound HTTP and used by the smoke test as `import httpx2`.
Use its `AsyncClient` context manager when a service needs HTTP; it manages connection cleanup.
