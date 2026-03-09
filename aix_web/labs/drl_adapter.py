"""Adapter for mounting the local DRL Flask app under ``/drl``."""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def _drl_config_from_env() -> dict:
    """Map ``DRL_*`` environment vars into the DRL app config contract."""

    keys = [
        "AIX_HUB_URL",
        "APP_TITLE",
    ]
    config: dict[str, str] = {}
    for key in keys:
        value = str(os.getenv(f"DRL_{key}", "")).strip()
        if value:
            config[key] = value
    return config


def load_drl_app():
    """Load and return the bridged DRL Flask application."""

    add_import_path("AIX_DRL_REPO", "../drl")
    module = import_module("drl_web")
    create_app = getattr(module, "create_app")
    config = _drl_config_from_env()
    return create_app(config if config else None)
