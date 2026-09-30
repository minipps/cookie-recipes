from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise

from {{ cookiecutter.module_name }}.api.routes import router
from {{ cookiecutter.module_name }}.db.config import TORTOISE_ORM


def create_app(database_url: str | None = None) -> FastAPI:
    config = TORTOISE_ORM
    if database_url is not None:
        config = {**config, "connections": {"default": database_url}}

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with RegisterTortoise(app, config=config):
            yield

    app = FastAPI(title={{ cookiecutter.project_name | tojson }}, lifespan=lifespan)
    app.include_router(router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
