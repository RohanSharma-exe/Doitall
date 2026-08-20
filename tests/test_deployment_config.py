from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_compose_waits_for_healthy_qdrant_and_restarts_api():
    compose = yaml.safe_load((PROJECT_ROOT / "docker-compose.yml").read_text())
    api = compose["services"]["api"]
    qdrant = compose["services"]["qdrant"]

    assert api["restart"] == "unless-stopped"
    assert api["depends_on"]["qdrant"]["condition"] == "service_healthy"

    healthcheck = qdrant["healthcheck"]
    assert healthcheck["test"] == [
        "CMD",
        "bash",
        "-c",
        ":> /dev/tcp/127.0.0.1/6333",
    ]
    assert healthcheck["retries"] > 0
    assert healthcheck["start_period"]
