FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.12.19 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-install-project
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev --no-editable

FROM python:3.13-slim AS runtime
WORKDIR /app
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1{% if cookiecutter.database == 'sqlite' %} \
    DATABASE_URL=sqlite:///data/db.sqlite3
{% endif %}

RUN useradd --uid 10001 --create-home app{% if cookiecutter.database == 'sqlite' %} && mkdir /data && chown app:app /data{% endif %}
COPY --from=builder /opt/venv /opt/venv
COPY --chmod=755 docker/entrypoint.sh /app/entrypoint.sh
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=3).close()"
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "{{ cookiecutter.module_name }}.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
