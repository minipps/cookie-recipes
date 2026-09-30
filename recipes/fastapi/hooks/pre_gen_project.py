import keyword
import re

project_slug = {{ cookiecutter.project_slug | tojson }}
module_name = {{ cookiecutter.module_name | tojson }}
description = {{ cookiecutter.description | tojson }}

if not re.fullmatch(r"[a-z][a-z0-9-]*", project_slug):
    raise SystemExit("project_slug must start with a lowercase letter and use a-z, 0-9, or -.")

if not re.fullmatch(r"[a-z][a-z0-9_]*", module_name) or keyword.iskeyword(module_name):
    raise SystemExit("module_name must be a lowercase Python identifier, not a keyword.")

if "\n" in description or "\r" in description:
    raise SystemExit("description must be a single line, as required by Python project metadata.")
