import unittest

import httpx2
from tortoise import Tortoise

from {{ cookiecutter.module_name }}.main import create_app


class ApiSmokeTest(unittest.IsolatedAsyncioTestCase):
    async def test_item_round_trip(self) -> None:
        app = create_app(database_url="sqlite://:memory:")
        async with app.router.lifespan_context(app):
            await Tortoise.generate_schemas()
            async with httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=app), base_url="http://test"
            ) as client:
                health = await client.get("/health")
                self.assertEqual(health.status_code, 200)
                self.assertEqual(health.json(), {"status": "ok"})

                created = await client.post("/api/v1/items", json={"name": " Example "})
                self.assertEqual(created.status_code, 201)
                item = created.json()
                self.assertEqual(item["name"], "Example")
                self.assertIsInstance(item["id"], int)

                fetched = await client.get(f"/api/v1/items/{item['id']}")
                self.assertEqual(fetched.status_code, 200)
                self.assertEqual(fetched.json(), item)

                missing = await client.get("/api/v1/items/999999")
                self.assertEqual(missing.status_code, 404)

                for name in ("", "   ", "x" * 201):
                    invalid = await client.post("/api/v1/items", json={"name": name})
                    self.assertEqual(invalid.status_code, 422)
