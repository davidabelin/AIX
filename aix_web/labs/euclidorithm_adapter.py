"""Adapter for mounting the external Euclidorithm Flask app.

Role
----
Attach the Euclidorithm app from the geometry workspace to the AIX hub. Unlike
``rps`` and ``c4``, Euclidorithm currently exposes a module-global Flask app
instead of a factory, so this adapter only resolves the import path and applies
light runtime overrides.
"""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def load_euclidorithm_app():
    """Load and return the bridged Euclidorithm Flask application.

    Notes
    -----
    The adapter honors ``EUCLID_FLASK_SECRET_KEY`` as a minimal override
    because the underlying app currently stores its Flask app object at module
    import time.
    """

    add_import_path("AIX_EUCLIDORITHM_REPO", "../geometry/euclidorithm")
    module = import_module("euclidorithm")
    app = getattr(module, "app")
    secret = str(os.getenv("EUCLID_FLASK_SECRET_KEY", "")).strip()
    if secret:
        app.config["SECRET_KEY"] = secret
    return app
