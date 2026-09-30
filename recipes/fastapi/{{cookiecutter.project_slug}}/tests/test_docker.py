import os
import subprocess
import unittest
from pathlib import Path
from uuid import uuid4

import httpx2


@unittest.skipUnless(os.environ.get("RUN_DOCKER_TESTS") == "1", "Set RUN_DOCKER_TESTS=1")
class DockerSmokeTest(unittest.TestCase):
    def test_database_survives_container_replacement(self) -> None:
        project = Path(__file__).resolve().parents[{{ 2 if cookiecutter._frontend else 1 }}]
        command = ["docker", "compose", "--project-name", f"smoke-{uuid4().hex[:12]}"]
        environment = {
            **os.environ,
            "PORT": "0",
{% if cookiecutter._frontend %}            "FRONTEND_PORT": "0",
{% endif %}            "POSTGRES_PORT": "0",
            "POSTGRES_PASSWORD": f"test:/?#@${uuid4().hex}",
        }

        def compose(*args: str) -> str:
            result = subprocess.run(  # noqa: S603 -- arguments are defined by this test
                [*command, *args],
                cwd=project,
                env=environment,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result.stdout.strip()

        try:
            compose("up", "--build", "--detach", "--wait", "--wait-timeout", "90")
            self.assertEqual(compose("exec", "-T", "api", "id", "-u"), "10001")
{% if cookiecutter._frontend %}            self.assertNotEqual(compose("exec", "-T", "frontend", "id", "-u"), "0")
            address = compose("port", "frontend", "8080")
            with httpx2.Client(base_url=f"http://{address}", trust_env=False) as client:
                page = client.get("/")
                self.assertEqual(page.status_code, 200)
                self.assertIn('id="app"', page.text)
                self.assertEqual(client.get("/client/side/route").text, page.text)
                self.assertEqual(client.get("/assets/missing.js").status_code, 404)
                self.assertEqual(client.get("/health").json(), {"status": "ok"})
{% else %}            address = compose("port", "api", "8000")
{% endif %}            with httpx2.Client(base_url=f"http://{address}", trust_env=False) as client:
                created = client.post("/api/v1/items", json={"name": "Persistent"})
                self.assertEqual(created.status_code, 201)
                item = created.json()

            compose("down")
            compose("up", "--detach", "--wait", "--wait-timeout", "90")
{% if cookiecutter._frontend %}            address = compose("port", "frontend", "8080")
{% else %}            address = compose("port", "api", "8000")
{% endif %}
            with httpx2.Client(base_url=f"http://{address}", trust_env=False) as client:
                response = client.get(f"/api/v1/items/{item['id']}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), item)
        except Exception:
            print(compose("logs", "--no-color"))
            raise
        finally:
            compose("down", "--volumes", "--remove-orphans", "--rmi", "local")
