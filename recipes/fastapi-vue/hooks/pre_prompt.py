"""Compose the shared backend and Vue overlay in Cookiecutter's temporary template copy."""

import shutil
from pathlib import Path

template = Path.cwd()
backend = template / "backend"
shutil.copytree(
    backend / "{{cookiecutter.project_slug}}",
    template / "{{cookiecutter.project_slug}}",
    dirs_exist_ok=True,
)
shutil.copy2(backend / "hooks" / "pre_gen_project.py", template / "hooks" / "pre_gen_project.py")
shutil.rmtree(backend)
