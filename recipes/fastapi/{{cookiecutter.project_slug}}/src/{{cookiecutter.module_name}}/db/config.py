import os

TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL", "sqlite://db.sqlite3")},
    "apps": {
        "models": {
            "models": ["{{ cookiecutter.module_name }}.db.models"],
            "default_connection": "default",
            "migrations": "{{ cookiecutter.module_name }}.db.migrations",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}
