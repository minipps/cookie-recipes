import os
import re
import subprocess
import tempfile
import tomllib
import unittest
from itertools import product
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter
from yaml import BaseLoader, load

RECIPE = Path(__file__).resolve().parents[1] / "recipes" / "fastapi"


class RecipeTest(unittest.TestCase):
    def run_command(self, project: Path, *args: str) -> str:
        result = subprocess.run(
            ["uv", *args],
            cwd=project,
            # Server-free gates use SQLite; Docker tests exercise the selected backend.
            env={
                **os.environ,
                "DATABASE_URL": "sqlite://db.sqlite3",
                "TEST_DATABASE_URL": "sqlite://:memory:",
            },
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_generated_projects(self) -> None:
        contexts = (
            ({}, "my_api"),
            (
                {
                    "project_name": "Cookie Service",
                    "module_name": "cookie_backend",
                    "description": 'An API with "quotes", apostrophes, and a backslash: \\.',
                    "database": "postgresql",
                },
                "cookie_backend",
            ),
        )
        for recipe, (context, module) in product(
            (RECIPE, RECIPE.with_name("fastapi-vue")), contexts
        ):
            if recipe.name == "fastapi-vue" and not context:
                module = "my_app"
            with (
                self.subTest(recipe=recipe.name, module=module),
                tempfile.TemporaryDirectory() as directory,
            ):
                project = Path(
                    cookiecutter(
                        str(recipe),
                        no_input=True,
                        output_dir=directory,
                        extra_context=context,
                        default_config={"replay_dir": directory},
                    )
                )
                frontend = recipe.name == "fastapi-vue"
                python_project = project / "backend" if frontend else project
                workflow_dir = project / ".github" / "workflows"
                ci = load((workflow_dir / "ci.yml").read_text(), Loader=BaseLoader)
                release_text = (workflow_dir / "release.yml").read_text()
                release = load(release_text, Loader=BaseLoader)
                self.assertIn("workflow_call", ci["on"])
                self.assertEqual(release["jobs"]["image"]["needs"], "gates")
                self.assertIn("${{ github.repository }}", release_text)
                self.assertIn("{{version}}", release_text)
                self.assertNotIn("{%", release_text)
                database = context.get("database", "sqlite")
                dependabot = load(
                    (project / ".github" / "dependabot.yml").read_text(), Loader=BaseLoader
                )
                ecosystems = {update["package-ecosystem"] for update in dependabot["updates"]}
                self.assertTrue({"uv", "docker", "github-actions"}.issubset(ecosystems))
                self.assertEqual("docker-compose" in ecosystems, database == "postgresql")
                self.assertEqual("npm" in ecosystems, frontend)
                self.assertEqual("frontend" in ci["jobs"], frontend)
                python_updates = next(
                    update
                    for update in dependabot["updates"]
                    if update["package-ecosystem"] == "uv"
                )
                self.assertEqual(python_updates["directory"], "/backend" if frontend else "/")
                if frontend:
                    self.assertFalse((project / "pyproject.toml").exists())
                    self.assertFalse((project / "src").exists())
                    self.assertFalse((project / "tests").exists())
                    self.assertTrue((python_project / "README.md").is_file())
                    self.assertTrue((python_project / ".python-version").is_file())
                    for job in ("python", "docker"):
                        self.assertEqual(
                            ci["jobs"][job]["defaults"]["run"]["working-directory"], "backend"
                        )
                    version_check = next(
                        step
                        for step in release["jobs"]["image"]["steps"]
                        if step.get("name") == "Check release version"
                    )
                    self.assertEqual(version_check["working-directory"], "backend")
                    image_matrix = release["jobs"]["image"]["strategy"]["matrix"]["include"]
                    self.assertEqual(
                        {image["dockerfile"] for image in image_matrix},
                        {"docker/Dockerfile", "docker/frontend.Dockerfile"},
                    )
                    # Both recipes render the same backend, rather than maintaining copies.
                    backend = Path(
                        cookiecutter(
                            str(RECIPE),
                            no_input=True,
                            output_dir=str(Path(directory) / "backend"),
                            extra_context={**context, "project_name": "My App"}
                            if not context
                            else context,
                            default_config={"replay_dir": directory},
                        )
                    )
                    for source in (backend / "src").rglob("*.py"):
                        self.assertEqual(
                            source.read_bytes(),
                            (python_project / source.relative_to(backend)).read_bytes(),
                        )
                    self.check_frontend(project)
                dependencies = tomllib.loads((python_project / "pyproject.toml").read_text())[
                    "project"
                ]["dependencies"]
                self.assertEqual(
                    any("[asyncpg]" in dependency for dependency in dependencies),
                    database == "postgresql",
                )
                compose = load((project / "compose.yml").read_text(), Loader=BaseLoader)
                self.assertEqual("db" in compose["services"], database == "postgresql")
                self.assertEqual("frontend" in compose["services"], frontend)
                self.run_command(python_project, "sync")
                for command in (
                    ("ruff", "format", "--check", "."),
                    ("ruff", "check", "."),
                    ("ty", "check"),
                    ("lint-imports", "--no-cache"),
                    ("tortoise", "init"),
                    ("tortoise", "makemigrations", "--name", "initial"),
                    ("tortoise", "migrate"),
                    ("tortoise", "migrate"),
                    ("lint-imports", "--no-cache"),
                    ("python", "-m", "unittest", "discover", "-s", "tests", "-v"),
                ):
                    self.run_command(python_project, "run", *command)
                self.assertTrue((python_project / "db.sqlite3").is_file())
                self.assertTrue(
                    list((python_project / "src" / module / "db" / "migrations").glob("0*.py"))
                )

                # A file-backed round trip verifies the migrated schema, not generate_schemas.
                self.run_command(
                    python_project,
                    "run",
                    "python",
                    "-c",
                    f"import asyncio; from {module}.main import create_app; "
                    f"from {module}.domain.items import ItemCreate; "
                    f"from {module}.services.items import create_item, get_item\n"
                    "async def check():\n"
                    "    app = create_app()\n"
                    "    async with app.router.lifespan_context(app):\n"
                    "        item = await create_item(ItemCreate(name='Migrated'))\n"
                    "        assert await get_item(item.id) == item\n"
                    "asyncio.run(check())\n",
                )

                for layer, dependency in (
                    ("api", f"{module}.db.models"),
                    ("api", "tortoise"),
                    ("db", f"{module}.api.routes"),
                    ("db", f"{module}.services.items"),
                    ("services", f"{module}.api.routes"),
                    ("domain", f"{module}.db.models"),
                    ("domain", "httpx2"),
                    ("services", f"{module}.main"),
                ):
                    with self.subTest(layer=layer, dependency=dependency):
                        violation = python_project / "src" / module / layer / "violation.py"
                        violation.write_text(f"import {dependency}\n", encoding="utf-8")
                        try:
                            result = subprocess.run(
                                ["uv", "run", "lint-imports", "--no-cache"],
                                cwd=python_project,
                                capture_output=True,
                                text=True,
                                timeout=60,
                                check=False,
                            )
                            self.assertNotEqual(result.returncode, 0, result.stdout)
                            self.assertIn("BROKEN", result.stdout)
                        finally:
                            violation.unlink()

    def test_invalid_names(self) -> None:
        for recipe, context in product(
            (RECIPE, RECIPE.with_name("fastapi-vue")),
            (
                {"project_slug": "../escape"},
                {"project_slug": "bad name"},
                {"module_name": "bad-name"},
                {"module_name": "class"},
                {"module_name": "123module"},
                {"description": "Two\nlines"},
            ),
        ):
            with (
                self.subTest(recipe=recipe.name, context=context),
                tempfile.TemporaryDirectory() as directory,
                self.assertRaises(FailedHookException),
            ):
                cookiecutter(
                    str(recipe),
                    no_input=True,
                    output_dir=directory,
                    extra_context=context,
                    default_config={"replay_dir": directory},
                )

    def test_vue_projects(self) -> None:
        recipe = RECIPE.with_name("vue")
        for context in ({}, {"project_name": "Vue <Demo>", "project_slug": "vue-demo"}):
            with self.subTest(context=context), tempfile.TemporaryDirectory() as directory:
                project = Path(
                    cookiecutter(
                        str(recipe),
                        no_input=True,
                        output_dir=directory,
                        extra_context=context,
                        default_config={"replay_dir": directory},
                    )
                )
                self.assertFalse((project / "pyproject.toml").exists())
                self.assertFalse((project / "src").exists())
                self.assertNotIn("proxy_pass", (project / "docker" / "nginx.conf").read_text())
                self.assertNotIn("server:", (project / "frontend" / "vite.config.ts").read_text())
                self.assertNotIn(
                    "/api/", (project / "frontend" / "src" / "stores" / "items.ts").read_text()
                )
                compose = load((project / "compose.yml").read_text(), Loader=BaseLoader)
                self.assertEqual(set(compose["services"]), {"frontend"})
                ci = load(
                    (project / ".github" / "workflows" / "ci.yml").read_text(), Loader=BaseLoader
                )
                self.assertEqual(set(ci["jobs"]), {"frontend", "docker"})
                self.assertIn("workflow_call", ci["on"])
                release = load(
                    (project / ".github" / "workflows" / "release.yml").read_text(),
                    Loader=BaseLoader,
                )
                self.assertEqual(release["jobs"]["image"]["needs"], "gates")
                dependabot = load(
                    (project / ".github" / "dependabot.yml").read_text(), Loader=BaseLoader
                )
                self.assertEqual(
                    {update["package-ecosystem"] for update in dependabot["updates"]},
                    {"npm", "docker", "github-actions"},
                )
                for file in ("package.json", "package-lock.json"):
                    self.assertEqual(
                        (project / "frontend" / file).read_bytes(),
                        (recipe / "{{cookiecutter.project_slug}}" / "frontend" / file).read_bytes(),
                    )
                self.check_frontend(project)
                if os.environ.get("RUN_DOCKER_TESTS") == "1":
                    self.check_vue_docker(project)

        for context in ({"project_slug": "../escape"}, {"project_slug": "bad name"}):
            with (
                self.subTest(context=context),
                tempfile.TemporaryDirectory() as directory,
                self.assertRaises(FailedHookException),
            ):
                cookiecutter(
                    str(recipe),
                    no_input=True,
                    output_dir=directory,
                    extra_context=context,
                    default_config={"replay_dir": directory},
                )

    def check_vue_docker(self, project: Path) -> None:
        command = ["docker", "compose", "--project-name", f"vue-{uuid4().hex[:12]}"]

        def compose(*args: str) -> str:
            result = subprocess.run(
                [*command, *args],
                cwd=project,
                env={**os.environ, "FRONTEND_PORT": "0"},
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result.stdout.strip()

        try:
            compose("up", "--build", "--detach", "--wait", "--wait-timeout", "90")
            self.assertNotEqual(compose("exec", "-T", "frontend", "id", "-u"), "0")
            address = compose("port", "frontend", "8080")
            client = build_opener(ProxyHandler({}))

            def get(path: str) -> str:
                with client.open(f"http://{address}{path}", timeout=10) as response:
                    return response.read().decode()

            page = get("/")
            self.assertIn('id="app"', page)
            self.assertEqual(get("/client/side/route"), page)
            script = re.search(r'src="([^"]+\.js)"', page)
            self.assertIsNotNone(script)
            self.assertTrue(get(script[1]))
            with self.assertRaises(HTTPError) as error:
                get("/assets/missing.js")
            self.assertEqual(error.exception.code, 404)
        except Exception:
            print(compose("logs", "--no-color"))
            raise
        finally:
            compose("down", "--volumes", "--remove-orphans", "--rmi", "local")

    def check_frontend(self, project: Path) -> None:
        def npm(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                ["npm", *args],
                cwd=project / "frontend",
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )

        for args in (
            ("ci", "--no-audit", "--no-fund"),
            *(
                ("run", command)
                for command in ("format:check", "lint", "type-check", "test", "knip", "build")
            ),
            ("run", "codemod", "--", "--help"),
            ("run", "codemod", "--", "--all", "--dry-run", "--include", "src/**/*.ts"),
        ):
            result = npm(*args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        violation = project / "frontend" / "src" / "violation.ts"
        violation.write_text("export const includes = ['a'].indexOf('a') !== -1;\n")
        try:
            result = npm("run", "lint")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("prefer-includes", result.stdout + result.stderr)
            result = npm("run", "knip")
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("violation.ts", result.stdout + result.stderr)
        finally:
            violation.unlink()


if __name__ == "__main__":
    unittest.main()
