"""Legacy route compatibility redirects into bridged RPS paths."""

from __future__ import annotations

from flask import Blueprint, redirect, request

routes_compat_bp = Blueprint("routes_compat", __name__)


def _redirect_with_query(target: str, *, code: int = 307):
    query = request.query_string.decode("utf-8")
    if query:
        target = f"{target}?{query}"
    return redirect(target, code=code)


@routes_compat_bp.get("/play")
def play_redirect():
    """Redirect legacy ``/play`` to ``/rps/play``."""

    return _redirect_with_query("/rps/play", code=302)


@routes_compat_bp.get("/training")
def training_redirect():
    """Redirect legacy ``/training`` to ``/rps/training``."""

    return _redirect_with_query("/rps/training", code=302)


@routes_compat_bp.get("/rl")
def rl_redirect():
    """Redirect legacy ``/rl`` to ``/rps/rl``."""

    return _redirect_with_query("/rps/rl", code=302)


@routes_compat_bp.route("/api/v1", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
@routes_compat_bp.route("/api/v1/", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def api_v1_root_redirect():
    """Bridge root-absolute API calls from legacy RPS frontend code."""

    return _redirect_with_query("/rps/api/v1", code=307)


@routes_compat_bp.route("/api/v1/<path:subpath>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def api_v1_redirect(subpath: str):
    """Bridge ``/api/v1/*`` calls to mounted RPS API paths."""

    return _redirect_with_query(f"/rps/api/v1/{subpath}", code=307)
