"""Adapter for mounting the external Euclidorithm Flask app."""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def load_euclidorithm_app():
    """Load and return the bridged Euclidorithm Flask application."""

    add_import_path("AIX_EUCLIDORITHM_REPO", "../geometry/euclidorithm")
    module = import_module("euclidorithm")
    app = getattr(module, "app")
    secret = str(os.getenv("EUCLID_FLASK_SECRET_KEY", "")).strip()
    if secret:
        app.config["SECRET_KEY"] = secret
    return app
