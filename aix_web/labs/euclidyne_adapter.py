"""Adapter for mounting the external Euclidyne Flask app.

Role
----
Attach the Euclidyne app from the geometry workspace to the AIX hub.
Euclidyne now ships as a standalone Flask repo rooted at
``../geometry/euclidyne`` with the WSGI entrypoint at ``euclidyne:app``.

Compatibility
-------------
The adapter still honors older AIX environment conventions so the umbrella can
bridge either the new Euclidyne package or an older Euclidorithm checkout
during transition.
"""

from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path

from aix_web.bridge import AIX_ROOT


def _candidate_import_roots() -> list[Path]:
    """Return candidate repo roots that may contain the Euclidyne entrypoint."""

    candidates: list[Path] = []
    for env_var in ("AIX_EUCLIDYNE_REPO", "AIX_EUCLIDORITHM_REPO"):
        override = str(os.getenv(env_var, "")).strip()
        if not override:
            continue
        repo_root = Path(override).expanduser().resolve()
        if (repo_root / "euclidyne.py").exists():
            candidates.append(repo_root)
        elif (repo_root / "euclidyne" / "euclidyne.py").exists():
            candidates.append(repo_root / "euclidyne")
        else:
            candidates.append(repo_root)

    candidates.append((AIX_ROOT / ".." / "geometry" / "euclidyne").resolve())
    candidates.append((AIX_ROOT / ".." / "geometry" / "euclidorithm").resolve())
    return candidates


def _ensure_import_root() -> None:
    """Insert the first existing Euclidyne import root into ``sys.path``."""

    for candidate in _candidate_import_roots():
        if not candidate.exists():
            continue
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        return
    raise ModuleNotFoundError(
        "Euclidyne repository not found. Set AIX_EUCLIDYNE_REPO or place the "
        "repo at ../geometry/euclidyne."
    )


def _apply_secret_override(app) -> None:
    """Override the bridged app secret key from AIX environment hints."""

    for key in ("EUCLIDYNE_FLASK_SECRET_KEY", "EUCLID_FLASK_SECRET_KEY", "FLASK_SECRET_KEY"):
        secret = str(os.getenv(key, "")).strip()
        if secret:
            app.config["SECRET_KEY"] = secret
            return


def load_euclidyne_app():
    """Load and return the bridged Euclidyne Flask application."""

    _ensure_import_root()
    try:
        module = import_module("euclidyne")
        app = getattr(module, "app")
    except ModuleNotFoundError as exc:
        if exc.name != "euclidyne":
            raise
        legacy_module = import_module("euclidorithm")
        app = getattr(legacy_module, "app")
    _apply_secret_override(app)
    return app
