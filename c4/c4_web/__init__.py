"""Minimal Flask app factory for c4 during migration bootstrap."""

from __future__ import annotations

from flask import Flask, jsonify


def create_app(config: dict | None = None) -> Flask:
    """Create a minimal c4 app instance.

    This is intentionally lightweight for the initial migration pass. Full
    route/template parity with `rps_web` is deferred.
    """

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_mapping(
        APP_NAME="c4",
        APP_TITLE="Connect4 Agent Lab",
    )
    if config:
        app.config.update(config)

    @app.get("/")
    def home():
        return jsonify(
            {
                "status": "ok",
                "service": "c4-web",
                "message": "c4 scaffold is initialized",
            }
        )

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "service": "c4-web"})

    return app
