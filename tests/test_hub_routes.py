from __future__ import annotations

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app, create_hub_app


@pytest.fixture(autouse=True)
def _stable_runtime_env(monkeypatch):
    monkeypatch.delenv("AIX_DISPATCH_SERVICE_LABS", raising=False)
    monkeypatch.delenv("AIX_ENABLED_LABS", raising=False)
    monkeypatch.delenv("GAE_ENV", raising=False)
    monkeypatch.delenv("K_SERVICE", raising=False)


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
    assert "/clue/" in html
    assert "/doubledigits/" in html
    assert "/euclidyne/" in html
    assert "/polyfolds/" in html


def test_healthz_reports_configured_and_pending_labs(client):
    response = client.get("/diagnostics/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert set(payload["configured_labs"]) == {"rps", "drl", "c4", "clue", "doubledigits", "euclidyne", "polyfolds"}
    assert set(payload["mounted_labs"]) == set()
    assert set(payload["deployed_service_labs"]) == set()
    assert set(payload["pending_labs"]) == {"rps", "drl", "c4", "clue", "doubledigits", "euclidyne", "polyfolds"}
    assert payload["failed_labs"] == {}


def test_legacy_healthz_alias_still_reports_local_health(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["service"] == "aix-hub"


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


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("/euclidorithm", "/euclidyne/"),
        ("/euclidorithm/", "/euclidyne/"),
        ("/euclidorithm/gear?driver_teeth=24&follower_teeth=40", "/euclidyne/gear?driver_teeth=24&follower_teeth=40"),
    ],
)
def test_legacy_euclidorithm_routes_redirect_to_euclidyne(client, path: str, target: str):
    response = client.get(path, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"].endswith(target)


def test_bridge_diagnostics_endpoint_exposes_config_snapshot(client):
    response = client.get("/diagnostics/bridges")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert "bridge_config" in payload
    assert set(payload["labs"].keys()) == {"rps", "drl", "c4", "clue", "doubledigits", "euclidyne", "polyfolds"}


def test_drl_portal_page_renders(monkeypatch):
    monkeypatch.setenv("AIX_DRL_APP_URL", "https://drl-web-x2ulcmhaiq-wm.a.run.app")
    app = create_app({"TESTING": True})
    mounted_client = Client(app, Response)
    response = mounted_client.get("/drl/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Deep RL Lab" in html
    assert "Table Of Contents" in html
    assert "https://drl-web-x2ulcmhaiq-wm.a.run.app" in html


def test_clue_mount_page_renders():
    app = create_app({"TESTING": True})
    mounted_client = Client(app, Response)
    response = mounted_client.get("/clue/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Multi-seat Clue" in html


def test_doubledigits_mount_page_renders():
    app = create_app({"TESTING": True})
    mounted_client = Client(app, Response)
    response = mounted_client.get("/doubledigits/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Single-digit Lab" in html
    assert "Arithmetic Lab" in html
    assert '"apiBase": "/doubledigits/api/v1"' in html


def test_doubledigits_mount_api_endpoints_remain_prefixed():
    app = create_app({"TESTING": True})
    mounted_client = Client(app, Response)

    examples_response = mounted_client.get("/doubledigits/api/v1/examples?level=single")
    assert examples_response.status_code == 200
    examples_payload = examples_response.get_json()
    assert examples_payload["level"] == "single"

    presets_response = mounted_client.get("/doubledigits/api/v1/presets?level=single")
    assert presets_response.status_code == 200
    presets_payload = presets_response.get_json()
    assert presets_payload["default_preset"] == "single_mnist_dense"


def test_euclidyne_mount_page_links_to_prefixed_sub_labs():
    app = create_app({"TESTING": True})
    mounted_client = Client(app, Response)
    response = mounted_client.get("/euclidyne/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'href="/euclidyne/quick"' in html
    assert 'href="/euclidyne/explorer"' in html
    assert 'href="/euclidyne/gear-ratio-forge"' in html


@pytest.mark.parametrize(
    "path",
    ["/", "/contact", "/privacy", "/toc"],
)
def test_aix_pages_include_footer_links(path: str):
    app = create_hub_app({"TESTING": True})
    client = app.test_client()
    response = client.get(path)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "copyleft.svg" in html
    assert "2026 AIX Protodyne" in html
    assert "Contact Us" in html
    assert "Privacy" in html
    assert "AIX TOC" in html


def test_toc_page_excludes_drl_but_lists_current_aix_arms():
    app = create_hub_app({"TESTING": True})
    client = app.test_client()
    response = client.get("/toc")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "AIX Table of Contents" in html
    assert "Sister DRL is intentionally excluded here." in html
    assert "/diagnostics/healthz" in html
    assert "/rps/play" in html
    assert "/c4/play" in html
    assert "/clue/" in html
    assert 'href="/clue/game"' not in html
    assert 'href="/clue/api/v1/games"' not in html
    assert "POST Create Game API" in html
    assert "/doubledigits/" in html
    assert 'href="/doubledigits/api/v1/infer"' not in html
    assert "POST Inference API" in html
    assert "/euclidyne/explorer" in html
    assert "/polyfolds/" in html


def test_contact_page_lists_clue_and_double_digits_issue_boxes(client):
    response = client.get("/contact")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "https://github.com/davidabelin/clue/issues" in html
    assert "https://github.com/davidabelin/dd/issues" in html


def test_healthz_cloud_warnings_when_db_persistence_missing(monkeypatch):
    monkeypatch.setenv("GAE_ENV", "standard")
    monkeypatch.setenv("AIX_DISPATCH_SERVICE_LABS", "drl")
    monkeypatch.delenv("RPS_DATABASE_URL", raising=False)
    monkeypatch.delenv("RPS_DATABASE_URL_SECRET", raising=False)
    monkeypatch.delenv("RPS_DB_SNAPSHOT_URI", raising=False)
    monkeypatch.delenv("C4_DATABASE_URL", raising=False)
    monkeypatch.delenv("C4_DATABASE_URL_SECRET", raising=False)
    monkeypatch.delenv("C4_DB_SNAPSHOT_URI", raising=False)
    monkeypatch.delenv("CLUE_DATABASE_URL", raising=False)
    monkeypatch.delenv("CLUE_DATABASE_URL_SECRET", raising=False)
    monkeypatch.delenv("CLUE_DB_SNAPSHOT_URI", raising=False)
    app = create_hub_app({"TESTING": True})
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    warnings = payload["runtime_warnings"]
    assert any("RPS persistence is not configured" in item for item in warnings)
    assert any("C4 persistence is not configured" in item for item in warnings)
    assert any("Clue persistence is not configured" in item for item in warnings)


def test_cloud_healthz_treats_default_lab_services_as_dispatched(monkeypatch):
    monkeypatch.setenv("GAE_ENV", "standard")
    monkeypatch.delenv("RPS_DB_SNAPSHOT_URI", raising=False)
    monkeypatch.delenv("C4_DB_SNAPSHOT_URI", raising=False)
    monkeypatch.delenv("CLUE_DB_SNAPSHOT_URI", raising=False)
    monkeypatch.delenv("RPS_DATABASE_URL", raising=False)
    monkeypatch.delenv("RPS_DATABASE_URL_SECRET", raising=False)
    monkeypatch.delenv("C4_DATABASE_URL", raising=False)
    monkeypatch.delenv("C4_DATABASE_URL_SECRET", raising=False)
    monkeypatch.delenv("CLUE_DATABASE_URL", raising=False)
    monkeypatch.delenv("CLUE_DATABASE_URL_SECRET", raising=False)
    app = create_hub_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/diagnostics/healthz")

    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload["deployed_service_labs"]) == {"rps", "c4", "clue", "doubledigits", "euclidyne", "polyfolds"}
    assert set(payload["pending_labs"]) == {"drl"}
    assert payload["runtime_warnings"] == []

    home_response = client.get("/")
    assert home_response.status_code == 200
    html = home_response.get_data(as_text=True)
    assert "Status: deployed service" in html
    assert "Open Clue" in html


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("/", "/polyfolds/"),
        ("/healthz", "/polyfolds/healthz"),
        ("/jobs?id=7", "/polyfolds/jobs?id=7"),
    ],
)
def test_polyfolds_service_host_redirects_into_polyfolds_mount(path: str, target: str):
    app = create_hub_app({"TESTING": True})
    client = app.test_client()
    response = client.get(path, headers={"Host": "polyfolds-dot-aix-labs.uw.r.appspot.com"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith(target)


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("/", "https://aix-labs.uw.r.appspot.com/clue/"),
        ("/admin?admin_token=test", "https://aix-labs.uw.r.appspot.com/clue/admin?admin_token=test"),
        ("/clue", "https://aix-labs.uw.r.appspot.com/clue/"),
        ("/clue/game?token=seat", "https://aix-labs.uw.r.appspot.com/clue/game?token=seat"),
    ],
)
def test_clue_service_host_redirects_to_canonical_aix_clue_path(path: str, target: str):
    app = create_hub_app({"TESTING": True})
    client = app.test_client()
    response = client.get(path, headers={"Host": "clue-dot-aix-labs.uw.r.appspot.com"}, follow_redirects=False)
    assert response.status_code == 301
    assert response.headers["Location"] == target
