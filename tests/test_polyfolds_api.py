from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app


def _client() -> Client:
    app = create_app({"TESTING": True})
    return Client(app, Response)


def test_polyfolds_presets_endpoint():
    client = _client()
    response = client.get("/polyfolds/api/v1/presets")
    assert response.status_code == 200
    payload = response.json
    assert set(payload["kinds"]) == {"dataset", "nets"}
    assert {"tetra", "hexa", "octa", "dodeca", "icosa"} <= set(payload["solids"])


def test_polyfolds_create_job_rejects_invalid_solid():
    client = _client()
    response = client.post(
        "/polyfolds/api/v1/jobs",
        json={"kind": "nets", "solid": "invalid_solid"},
    )
    assert response.status_code == 400
    payload = response.json
    assert payload is not None
    assert "solid must be one of" in payload["error"]


def test_polyfolds_list_jobs_endpoint():
    client = _client()
    response = client.get("/polyfolds/api/v1/jobs")
    assert response.status_code == 200
    payload = response.json
    assert isinstance(payload["jobs"], list)

