"""Adapter for mounting the standalone Double-digits app under ``/doubledigits``."""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def _doubledigits_config_from_env() -> dict:
    keys = [
        "MODELS_DIR",
        "DATA_DIR",
        "ARTIFACT_CACHE",
    ]
    config: dict[str, str | bool] = {}
    for key in keys:
        value = str(os.getenv(f"DOUBLEDIGITS_{key}", "")).strip()
        if not value:
            continue
        config[f"DOUBLEDIGITS_{key}"] = value
    return config


def load_doubledigits_app():
    add_import_path("AIX_DOUBLEDIGITS_REPO", "../dd")
    module = import_module("dd_web")
    create_app = getattr(module, "create_app")
    config = _doubledigits_config_from_env()
    return create_app(config if config else None)
