import re
import sys

if not re.fullmatch(r"[a-z][a-z0-9-]*", {{cookiecutter.project_slug | tojson}}):
    print(
        "project_slug must start with a lowercase letter and contain only lowercase letters, digits, or hyphens."
    )
    sys.exit(1)
