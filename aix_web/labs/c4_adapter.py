"""Adapter for mounting the c4 Flask app under ``/c4``."""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def _c4_config_from_env() -> dict:
    """Map ``C4_*`` environment vars into the c4 app config contract."""

    keys = [
        "DATABASE_URL",
        "DATABASE_URL_SECRET",
        "DB_PATH",
        "EVENTS_DIR",
        "MODELS_DIR",
        "EXPORTS_DIR",
        "DEFAULT_AGENT",
        "TRAINING_EXECUTION_MODE",
        "TASKS_PROJECT_ID",
        "TASKS_LOCATION",
        "TASKS_QUEUE",
        "TRAINING_WORKER_URL",
        "TRAINING_WORKER_TOKEN",
        "TRAINING_WORKER_TOKEN_SECRET",
        "TRAINING_WORKER_SERVICE_ACCOUNT",
        "INTERNAL_WORKER_TOKEN",
        "INTERNAL_WORKER_TOKEN_SECRET",
    ]
    config: dict[str, str] = {}
    for key in keys:
        value = str(os.getenv(f"C4_{key}", "")).strip()
        if value:
            config[key] = value
    return config


def load_c4_app():
    """Load and return the bridged c4 Flask application."""

    add_import_path("AIX_C4_REPO", r"c4")
    module = import_module("c4_web")
    create_app = getattr(module, "create_app")
    config = _c4_config_from_env()
    return create_app(config if config else None)
