#!/bin/sh
set -eu

tortoise -c {{ cookiecutter.module_name }}.db.config.TORTOISE_ORM migrate
exec "$@"
