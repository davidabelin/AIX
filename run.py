"""Local entrypoint for the AIX umbrella web app."""

from __future__ import annotations

from werkzeug.serving import run_simple

from aix_web import create_app


app = create_app()


if __name__ == "__main__":
    run_simple("127.0.0.1", 5000, app, use_debugger=True, use_reloader=True)

