from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from doitall.api.app import create_app
from doitall.services.registry import container


class FakeProvider:
    name = "fake"

    async def available_models(self):
        return ["fake-fast", "fake-smart"]


class FakeProviderManager:
    def all(self):
        return [FakeProvider()]


class FakeSkill:
    name = "fake_skill"
    description = "Fake skill"
    version = "1.2.3"
    enabled = True

    @classmethod
    def definition(cls):
        definition = MagicMock()
        definition.input_schema = {"type": "object"}
        return definition


class FakeSkillRegistry:
    def all(self):
        return [FakeSkill]


def test_system_routes_list_models_skills_and_estimate_tokens():
    container.clear()
    container.register("provider_manager", FakeProviderManager())
    container.register("skill_registry", FakeSkillRegistry())

    with (
        patch("doitall.api.app.bootstrap", return_value=None),
        patch("doitall.api.app.async_bootstrap", new=AsyncMock(return_value=None)),
        patch("doitall.api.app.cleanup", return_value=None),
    ):
        app = create_app()
        with TestClient(app) as client:
            models = client.get("/v1/models")
            skills = client.get("/v1/skills")
            tokens = client.post("/v1/tokens/estimate", json={"text": "hello world"})

    assert models.status_code == 200
    assert {model["model"] for model in models.json()["models"]} == {
        "fake-fast",
        "fake-smart",
    }
    assert skills.status_code == 200
    assert skills.json()["skills"][0]["name"] == "fake_skill"
    assert tokens.status_code == 200
    assert tokens.json()["estimated_tokens"] == 3
