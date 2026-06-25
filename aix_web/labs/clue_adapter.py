"""Adapter for mounting the standalone clue Flask app under ``/clue``."""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def _clue_config_from_env() -> dict:
    """Map ``CLUE_*`` environment vars into the Clue app config contract."""

    keys = [
        "DATABASE_URL",
        "DATABASE_URL_SECRET",
        "DB_PATH",
        "DB_SNAPSHOT_URI",
        "SECRET_KEY",
        "INTERNAL_WORKER_TOKEN",
    ]
    config: dict[str, str] = {}
    for key in keys:
        value = str(os.getenv(f"CLUE_{key}", "")).strip()
        if value:
            config[key] = value
    return config


def load_clue_app():
    """Load and return the bridged Clue Flask application."""

    add_import_path("AIX_CLUE_REPO", "../clue")
    module = import_module("clue_web")
    create_app = getattr(module, "create_app")
    config = _clue_config_from_env()
    return create_app(config if config else None)
