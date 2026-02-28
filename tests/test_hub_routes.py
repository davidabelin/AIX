from __future__ import annotations

import pytest

from aix_web import create_hub_app


@pytest.fixture
def app():
    app = create_hub_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_hub_home_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Assorted Artificial Intelligence Labs" in html
    assert "/rps/" in html
    assert "/euclidorithm/" in html
    assert "/polyfolds/" in html


def test_healthz_reports_configured_and_pending_labs(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert set(payload["configured_labs"]) == {"rps", "euclidorithm", "polyfolds"}
    assert set(payload["mounted_labs"]) == set()
    assert set(payload["pending_labs"]) == {"rps", "euclidorithm", "polyfolds"}
    assert payload["failed_labs"] == {}


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("/play", "/rps/play"),
        ("/training", "/rps/training"),
        ("/rl", "/rps/rl"),
    ],
)
def test_legacy_routes_redirect_to_rps(client, path: str, target: str):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith(target)

