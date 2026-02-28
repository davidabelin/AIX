"""Placeholder Polyfolds lab app mounted under ``/polyfolds``."""

from __future__ import annotations

from flask import Flask, jsonify, render_template


def load_polyfolds_app() -> Flask:
    """Return a lightweight Polyfolds web shell for phased integration."""

    app = Flask(
        "aix_polyfolds",
        template_folder="../templates",
        static_folder="../static",
    )

    @app.get("/")
    def polyfolds_home() -> str:
        return render_template(
            "pages/polyfolds_home.html",
            title="Polyfolds",
        )

    @app.get("/healthz")
    def polyfolds_healthz():
        return jsonify(
            {
                "status": "ok",
                "service": "polyfolds-adapter",
                "phase": "placeholder",
            }
        )

    return app

