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

