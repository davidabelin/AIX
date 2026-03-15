"""Adapter for mounting the external RPS Flask app under ``/rps``.

Role
----
Bridge the standalone ``rps`` repo into the local AIX hub by resolving the
sibling repository, importing its app factory, and translating ``RPS_*``
environment variables into the config contract expected by ``rps_web``.
"""

from __future__ import annotations

import os
from importlib import import_module

from aix_web.bridge import add_import_path


def _rps_config_from_env() -> dict:
    """Map ``RPS_*`` environment vars into the RPS app config contract.

    Cross-Repo Context
    ------------------
    This keeps AIX deployment and local dev settings aligned with the standalone
    ``rps`` service without forcing AIX to know the internals of that repo's
    configuration loader.
    """

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
        "ROUND_EVENT_LOGGING_MODE",
        "LATENCY_EVENT_LOGGING_MODE",
    ]
    config: dict[str, str] = {}
    for key in keys:
        value = str(os.getenv(f"RPS_{key}", "")).strip()
        if value:
            config[key] = value
    return config


def load_rps_app():
    """Load and return the bridged RPS Flask application.

    Role
    ----
    Resolve the ``rps`` repo location, import ``rps_web.create_app``, and apply
    any translated config overrides supplied from the AIX environment.
    """

    add_import_path("AIX_RPS_REPO", "../rps")
    module = import_module("rps_web")
    create_app = getattr(module, "create_app")
    config = _rps_config_from_env()
    return create_app(config if config else None)
