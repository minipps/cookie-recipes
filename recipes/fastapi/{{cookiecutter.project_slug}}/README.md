# {{ cookiecutter.project_name }}

{{ cookiecutter.description }}

## Run

```sh
{% if cookiecutter.database == 'postgresql' %}export POSTGRES_PASSWORD="$(openssl rand -hex 32)"
docker compose up --detach --wait db
{% endif %}
uv sync
uv run tortoise init
uv run tortoise makemigrations --name initial
uv run tortoise migrate
uv run uvicorn {{ cookiecutter.module_name }}.main:create_app --factory --reload
```

Open http://127.0.0.1:8000/docs. `GET /health` checks that the process is serving.
`POST /api/v1/items` accepts `{"name": "Example"}`; `GET /api/v1/items/1` reads it back.
These example routes are unauthenticated; replace them with your application's endpoints.

{% if cookiecutter.database == 'postgresql' %}This project uses PostgreSQL with the asyncpg driver already installed. The command above
starts PostgreSQL 18 for local development. Keep the same password when restarting the stack.
Defaults are `POSTGRES_HOST=localhost`, `POSTGRES_PORT=5432`, `POSTGRES_USER=app`, and
`POSTGRES_DB=app`; set `POSTGRES_PASSWORD` before running migrations or the API.
These settings are passed separately so passwords do not need URL encoding.

Set `DATABASE_URL` to use another database, for example a hosted `postgres://` connection URL.
Passwords in a connection URL must be URL encoded. Compose uses the separate `POSTGRES_*`
settings and connects to the `db` service; set host shell variables or put them in `.env` for
Compose. The Python process reads exported variables directly and does not load `.env` files.
{% else %}SQLite is stored in `db.sqlite3` by default. Set `DATABASE_URL` to override the connection URL
for both the API and migration commands. Environment variables are read directly; `.env` files
are not loaded automatically.
{% endif %}

Commit `uv.lock` after `uv sync` and commit generated migrations. After editing models:

```sh
uv run tortoise makemigrations --name describe_change
uv run tortoise migrate
```

Apply migrations before starting the API. Startup opens connections without creating or
changing tables. API tests default to disposable in-memory SQLite. Set `TEST_DATABASE_URL`
to exercise another disposable test database; the smoke test creates tables and inserts a record.
{% if cookiecutter.database == 'postgresql' %}GitHub CI provides a separate PostgreSQL test database and sets that URL automatically.
{% endif %}

## Docker with {{ 'PostgreSQL' if cookiecutter.database == 'postgresql' else 'SQLite' }}

Run the initial setup above to create `uv.lock` and migrations, then:

```sh
docker compose up --build --detach --wait
docker compose logs --follow api
docker compose down
```

The API listens on http://127.0.0.1:8000. Set `PORT` to change the host port.
{% if cookiecutter.database == 'postgresql' %}Compose runs the non-root API container and a health-checked PostgreSQL service.
Set `POSTGRES_PASSWORD` before starting; the API waits for PostgreSQL to become healthy.
PostgreSQL stores its data in the named `postgres-data` volume at `/var/lib/postgresql`.
The database is published on localhost only; `POSTGRES_PORT` changes the host port.
{% else %}The non-root container stores SQLite at `/data/db.sqlite3` in the named `data` volume.
{% endif %}
Stopping or replacing containers preserves this volume; `docker compose down --volumes`
deletes it. The image excludes local databases, secrets, development tools, and test files.

The container applies committed Tortoise migrations before starting the API and exits if
migration fails. Generate new migrations locally, commit them, and rebuild after model changes.
{% if cookiecutter.database == 'sqlite' %}Run one API container against this SQLite volume.

To build without Compose:

```sh
docker build --file docker/Dockerfile --tag {{ cookiecutter.project_slug }} .
docker run --rm --publish 127.0.0.1:8000:8000 --mount type=volume,src={{ cookiecutter.project_slug }}-data,dst=/data {{ cookiecutter.project_slug }}
```
{% endif %}

## Quality checks

```sh
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run lint-imports
uv run python -m unittest discover -s tests -v
```

To also build the image and verify that database records survive container replacement:

```sh
RUN_DOCKER_TESTS=1 uv run python -m unittest discover -s tests -v
```

This requires Docker with Compose and the initial lockfile and migrations. The test uses a
temporary Compose project and port and removes its containers, image, and volume afterward.

Use `uv run ruff format .` and `uv run ruff check --fix .` to apply formatting and safe lint fixes.

## GitHub CI and releases

Commit `uv.lock` and the initial migrations before pushing the generated project to GitHub.
`.github/workflows/ci.yml` runs formatting, Ruff, ty, import-linter, API tests, and the Docker
persistence test on pushes to `main` and pull requests. Installs use `uv sync --locked`, so a
missing or stale lockfile fails CI.

The release workflow runs the same gates, then publishes the image to
`ghcr.io/<owner>/<repository>` using GitHub's built-in token. No registry secret is needed.
To release, update `project.version` in `pyproject.toml`, run `uv lock`, commit and push the
changes, then push a matching stable version tag:

```sh
git tag v0.1.0
git push origin v0.1.0
```

The tag must match the project version. Stable releases receive version, major/minor, and
`latest` image tags. Publishing an image does not deploy it to a server; pull and run the
desired version with the same persistent database volume.

## Architecture

```text
src/{{ cookiecutter.module_name }}/
  main.py         # composition root: FastAPI, routers, ORM lifespan
  api/            # HTTP routes; calls services, never imports storage directly
  services/       # application operations; calls storage, returns domain schemas
  db/             # Tortoise models, configuration, generated migrations
  domain/         # shared Pydantic schemas; no application or I/O imports
tests/            # HTTPX2 ASGI smoke test and optional Docker persistence test
```

Import-linter allows API → services → DB while rejecting direct API → DB imports and
reverse dependencies. Type-checking imports are checked too. Application layers cannot
import `main`, which wires them together.

HTTPX2 is installed for outbound HTTP and used by the smoke test as `import httpx2`.
Use its `AsyncClient` context manager when a service needs HTTP; it manages connection cleanup.
