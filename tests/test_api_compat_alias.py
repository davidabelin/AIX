from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app


def test_legacy_api_alias_returns_json_without_redirect():
    app = create_app({"TESTING": True})
    client = Client(app, Response)
    response = client.get("/api/v1/agents", follow_redirects=False)
    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("application/json")
    payload = response.json
    assert payload is not None
    assert isinstance(payload.get("agents"), list)
