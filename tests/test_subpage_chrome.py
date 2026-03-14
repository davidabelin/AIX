from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app


def test_polyfolds_page_includes_global_back_link():
    app = create_app({"TESTING": True})
    client = Client(app, Response)
    response = client.get("/polyfolds/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="aix-subpage-back"' in html
    assert "Back to AIX Hub" in html


def test_all_lab_home_pages_include_global_back_link():
    app = create_app({"TESTING": True})
    client = Client(app, Response)
    palette_by_path = {
        "/rps/": "#0f7b6d",
        "/drl/": "#9a4d1a",
        "/c4/": "#8a1f2f",
        "/euclidorithm/": "#0a4f8b",
        "/polyfolds/": "#2f7d32",
    }
    for path, accent in palette_by_path.items():
        response = client.get(path)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'id="aix-subpage-back"' in html
        assert "Back to AIX Hub" in html
        assert f"--accent: {accent}" in html
