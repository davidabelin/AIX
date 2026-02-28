"""Legacy route compatibility redirects into bridged RPS paths."""

from __future__ import annotations

from flask import Blueprint, redirect

routes_compat_bp = Blueprint("routes_compat", __name__)


@routes_compat_bp.get("/play")
def play_redirect():
    """Redirect legacy ``/play`` to ``/rps/play``."""

    return redirect("/rps/play", code=302)


@routes_compat_bp.get("/training")
def training_redirect():
    """Redirect legacy ``/training`` to ``/rps/training``."""

    return redirect("/rps/training", code=302)


@routes_compat_bp.get("/rl")
def rl_redirect():
    """Redirect legacy ``/rl`` to ``/rps/rl``."""

    return redirect("/rps/rl", code=302)

