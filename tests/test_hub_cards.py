from __future__ import annotations

import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app, create_hub_app
from aix_web.lazy_mount import LazyMountApp


@pytest.fixture(autouse=True)
def _stable_runtime_env(monkeypatch):
    monkeypatch.delenv("AIX_DISPATCH_SERVICE_LABS", raising=False)
    monkeypatch.delenv("AIX_ENABLED_LABS", raising=False)
    monkeypatch.delenv("GAE_ENV", raising=False)
    monkeypatch.delenv("K_SERVICE", raising=False)


def _set_sibling_repos(monkeypatch, found):
    """Pretend every sibling lab checkout is present (a path) or missing (None)."""

    monkeypatch.setattr("aix_web.lab_registry.resolve_repo_path", lambda *_args: found)
    monkeypatch.setattr("aix_web.labs.euclidyne_adapter.find_euclidyne_root", lambda: found)


def test_hub_cards_show_categories_quick_links_and_surprise(monkeypatch, tmp_path):
    _set_sibling_repos(monkeypatch, tmp_path)
    client = create_hub_app({"TESTING": True}).test_client()

    html = client.get("/").get_data(as_text=True)

    assert "Surprise me" in html
    assert 'data-filter="games"' in html
    assert 'data-category="games" data-slug="rps"' in html
    assert 'href="/rps/play"' in html
    assert 'href="/c4/arena"' in html
    assert 'href="/euclidyne/explorer"' in html
    # JSON APIs and lab home pages are not repeated as shortcut chips.
    assert 'href="/euclidyne/api/v2/euclid"' not in html
    assert "Not installed here" not in html
    assert "<strong>7</strong> open right now" in html


def test_missing_sibling_repo_shows_install_hint_instead_of_link(monkeypatch):
    _set_sibling_repos(monkeypatch, None)
    client = create_hub_app({"TESTING": True}).test_client()

    html = client.get("/").get_data(as_text=True)

    assert "Not installed here" in html
    assert "Clone the rps repo next to AIX" in html
    assert 'href="/rps/play"' not in html
    assert "Open Deep RL Lab" in html
    assert "Open Polyfolds" in html


def test_missing_sibling_repo_keeps_install_hint_after_failed_load(monkeypatch):
    _set_sibling_repos(monkeypatch, None)
    client = Client(create_app({"TESTING": True}), Response)

    assert client.get("/rps/").status_code == 503
    html = client.get("/").get_data(as_text=True)

    assert "Having trouble" not in html
    assert "Clone the rps repo next to AIX" in html


def test_surprise_redirects_only_to_openable_labs(monkeypatch):
    _set_sibling_repos(monkeypatch, None)
    client = create_hub_app({"TESTING": True}).test_client()

    targets = {client.get("/surprise").headers["Location"] for _ in range(40)}

    assert targets <= {"/drl/", "/polyfolds/"}
    assert targets


def test_surprise_falls_back_to_hub_when_nothing_is_open(monkeypatch):
    _set_sibling_repos(monkeypatch, None)
    monkeypatch.setenv("AIX_ENABLED_LABS", "rps")
    client = create_hub_app({"TESTING": True}).test_client()

    response = client.get("/surprise")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert "btn-surprise" not in client.get("/").get_data(as_text=True)


def test_unknown_page_gets_friendly_404():
    client = create_hub_app({"TESTING": True}).test_client()

    response = client.get("/no-such-page", headers={"Accept": "text/html"})

    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "latent space" in html
    assert "<code>/no-such-page</code>" in html
    assert "2026 AIX Protodyne" in html


def test_unknown_api_path_gets_json_404():
    client = create_hub_app({"TESTING": True}).test_client()

    response = client.get("/diagnostics/nope", headers={"Accept": "application/json"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "not found", "path": "/diagnostics/nope"}


def test_unavailable_lab_page_explains_how_to_fix():
    def _broken_loader():
        raise ModuleNotFoundError("No module named '<rps_web>'")

    app = LazyMountApp(name="rps", loader=_broken_loader, hint="Clone the rps repo next to AIX.")
    response = Client(app, Response).get("/")

    assert response.status_code == 503
    assert response.headers["Content-Type"].startswith("text/html")
    html = response.get_data(as_text=True)
    assert "Clone the rps repo next to AIX." in html
    assert "&lt;rps_web&gt;" in html
    assert 'href="/"' in html
