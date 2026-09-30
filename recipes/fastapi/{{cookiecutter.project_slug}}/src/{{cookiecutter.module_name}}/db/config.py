import os

TORTOISE_ORM = {
{% if cookiecutter.database == 'postgresql' %}    "connections": {
        "default": os.environ.get("DATABASE_URL")
        or {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.environ.get("POSTGRES_HOST", "localhost"),
                "port": int(os.environ.get("POSTGRES_PORT", "5432")),
                "user": os.environ.get("POSTGRES_USER", "app"),
                "password": os.environ.get("POSTGRES_PASSWORD", ""),
                "database": os.environ.get("POSTGRES_DB", "app"),
            },
        },
    },
{% else %}    "connections": {"default": os.environ.get("DATABASE_URL", "sqlite://db.sqlite3")},
{% endif %}    "apps": {
        "models": {
            "models": ["{{ cookiecutter.module_name }}.db.models"],
            "default_connection": "default",
            "migrations": "{{ cookiecutter.module_name }}.db.migrations",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}
