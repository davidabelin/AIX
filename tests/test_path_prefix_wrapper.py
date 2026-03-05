from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web.path_prefix_wrapper import PathPrefixWrapper


def _echo_path_app(environ, start_response):
    body = environ.get("PATH_INFO", "").encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]


def test_path_prefix_wrapper_prepends_prefix_for_nested_path():
    wrapped = PathPrefixWrapper(_echo_path_app, prefix="/api/v1")
    client = Client(wrapped, Response)
    response = client.get("/agents")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "/api/v1/agents"


def test_path_prefix_wrapper_prepends_prefix_for_root_path():
    wrapped = PathPrefixWrapper(_echo_path_app, prefix="/api/v1")
    client = Client(wrapped, Response)
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "/api/v1"
