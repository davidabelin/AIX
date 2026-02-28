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


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("/api/v1/agents", "/rps/api/v1/agents"),
        ("/api/v1/rl/status", "/rps/api/v1/rl/status"),
        ("/api/v1/benchmarks/suites", "/rps/api/v1/benchmarks/suites"),
    ],
)
def test_api_routes_redirect_to_rps_with_307(client, path: str, target: str):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"].endswith(target)


def test_api_post_redirect_preserves_method(client):
    response = client.post("/api/v1/games", json={"agent": "markov"}, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"].endswith("/rps/api/v1/games")
