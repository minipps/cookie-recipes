import subprocess
import tempfile
import unittest
from pathlib import Path

from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

RECIPE = Path(__file__).resolve().parents[1] / "recipes" / "fastapi"


class RecipeTest(unittest.TestCase):
    def run_command(self, project: Path, *args: str) -> str:
        result = subprocess.run(
            ["uv", *args],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=180,
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
                },
                "cookie_backend",
            ),
        )
        for context, module in contexts:
            with (
                self.subTest(module=module),
                tempfile.TemporaryDirectory() as directory,
            ):
                project = Path(
                    cookiecutter(
                        str(RECIPE),
                        no_input=True,
                        output_dir=directory,
                        extra_context=context,
                        default_config={"replay_dir": directory},
                    )
                )
                self.run_command(project, "sync")
                for command in (
                    ("ruff", "format", "--check", "."),
                    ("ruff", "check", "."),
                    ("ty", "check"),
                    ("lint-imports", "--no-cache"),
                    ("python", "-m", "unittest", "discover", "-s", "tests", "-v"),
                    ("tortoise", "init"),
                    ("tortoise", "makemigrations", "--name", "initial"),
                    ("tortoise", "migrate"),
                    ("tortoise", "migrate"),
                    ("lint-imports", "--no-cache"),
                ):
                    self.run_command(project, "run", *command)
                self.assertTrue((project / "db.sqlite3").is_file())
                self.assertTrue(
                    list((project / "src" / module / "db" / "migrations").glob("0*.py"))
                )

                # A file-backed round trip verifies the migrated schema, not generate_schemas.
                self.run_command(
                    project,
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
                        violation = project / "src" / module / layer / "violation.py"
                        violation.write_text(f"import {dependency}\n", encoding="utf-8")
                        try:
                            result = subprocess.run(
                                ["uv", "run", "lint-imports", "--no-cache"],
                                cwd=project,
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
        for context in (
            {"project_slug": "../escape"},
            {"project_slug": "bad name"},
            {"module_name": "bad-name"},
            {"module_name": "class"},
            {"module_name": "123module"},
            {"description": "Two\nlines"},
        ):
            with (
                self.subTest(context=context),
                tempfile.TemporaryDirectory() as directory,
                self.assertRaises(FailedHookException),
            ):
                cookiecutter(
                    str(RECIPE),
                    no_input=True,
                    output_dir=directory,
                    extra_context=context,
                    default_config={"replay_dir": directory},
                )


if __name__ == "__main__":
    unittest.main()
