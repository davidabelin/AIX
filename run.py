"""Local entrypoint for the AIX umbrella web app.

Usage::

    python run.py                  # http://127.0.0.1:5000/
    python run.py --port 8080      # pick another port (or set PORT)
    python run.py --host 0.0.0.0   # listen on your LAN (or set AIX_HOST)
    python run.py --no-reload      # skip the auto-reloader
"""

from __future__ import annotations

import argparse
import os

from werkzeug.serving import run_simple

from aix_web import create_app
from aix_web.lab_registry import build_lab_specs


app = create_app()


def _print_lab_summary(url: str) -> None:
    """Print which labs have a local checkout, so missing repos are obvious."""

    print(f"\n  AIX Labs is starting at {url}\n")
    for spec in build_lab_specs():
        if not spec.enabled:
            mark, note = "[off]", "disabled via AIX_ENABLED_LABS"
        elif spec.locate_source is None:
            mark, note = "[ok] ", "built into AIX"
        elif (found := spec.locate_source()) is not None:
            mark, note = "[ok] ", str(found)
        else:
            mark, note = "[--] ", f"not found. {spec.install_hint}"
        print(f"  {mark} /{spec.slug + '/':<15} {note}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AIX hub locally.")
    parser.add_argument("--host", default=os.getenv("AIX_HOST", "127.0.0.1"), help="interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "5000")), help="port to listen on (default: 5000)")
    parser.add_argument("--no-reload", action="store_true", help="disable the auto-reloader")
    args = parser.parse_args()

    # The reloader re-runs this module in a child process; only greet once.
    if os.getenv("WERKZEUG_RUN_MAIN") != "true":
        shown_host = "127.0.0.1" if args.host in {"0.0.0.0", "::"} else args.host
        _print_lab_summary(f"http://{shown_host}:{args.port}/")

    run_simple(args.host, args.port, app, use_debugger=True, use_reloader=not args.no_reload)


if __name__ == "__main__":
    main()
