from __future__ import annotations

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app, create_hub_app


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
    assert "/drl/" in html
    assert "/c4/" in html
    assert "/euclidorithm/" in html
    assert "/polyfolds/" in html


def test_healthz_reports_configured_and_pending_labs(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert set(payload["configured_labs"]) == {"rps", "drl", "c4", "euclidorithm", "polyfolds"}
    assert set(payload["mounted_labs"]) == set()
    assert set(payload["pending_labs"]) == {"rps", "drl", "c4", "euclidorithm", "polyfolds"}
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


def test_bridge_diagnostics_endpoint_exposes_config_snapshot(client):
    response = client.get("/diagnostics/bridges")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert "bridge_config" in payload
    assert set(payload["labs"].keys()) == {"rps", "drl", "c4", "euclidorithm", "polyfolds"}


def test_drl_portal_page_renders(client):
    app = create_app({"TESTING": True})
    mounted_client = Client(app, Response)
    response = mounted_client.get("/drl/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Deep RL Lab" in html
    assert "Table Of Contents" in html
    assert "AIX_DRL_APP_URL" in html


def test_healthz_cloud_warnings_when_db_persistence_missing(monkeypatch):
    monkeypatch.setenv("GAE_ENV", "standard")
    monkeypatch.delenv("RPS_DATABASE_URL", raising=False)
    monkeypatch.delenv("RPS_DATABASE_URL_SECRET", raising=False)
    monkeypatch.delenv("C4_DATABASE_URL", raising=False)
    monkeypatch.delenv("C4_DATABASE_URL_SECRET", raising=False)
    app = create_hub_app({"TESTING": True})
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    warnings = payload["runtime_warnings"]
    assert any("RPS persistence is not configured" in item for item in warnings)
    assert any("C4 persistence is not configured" in item for item in warnings)
