"""AIX app factory and WSGI dispatcher wiring."""

from __future__ import annotations

from flask import Flask, redirect, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from aix_web.blueprints.hub import hub_bp
from aix_web.blueprints.routes_compat import routes_compat_bp
from aix_web.lab_registry import build_lab_specs, resolve_lab_mounts
from aix_web.lab_theme_wrapper import LabThemeWrapper
from aix_web.path_prefix_wrapper import PathPrefixWrapper


def create_hub_app(config: dict | None = None) -> Flask:
    """Create the hub Flask app used as the root AIX shell."""

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_mapping(
        HUB_TITLE="AIX: Assorted Artificial Intelligence Labs",
    )
    if config:
        app.config.update(config)

    @app.before_request
    def redirect_polyfolds_service_host():
        host = (request.host or "").split(":", 1)[0].lower()
        if host != "polyfolds-dot-aix-labs.uw.r.appspot.com":
            return None
        path = request.path or "/"
        if path.startswith("/polyfolds"):
            return None
        target = "/polyfolds/" if path == "/" else f"/polyfolds{path}"
        if request.query_string:
            target = f"{target}?{request.query_string.decode('utf-8', errors='ignore')}"
        return redirect(target, code=302)

    specs = build_lab_specs()
    mounts = resolve_lab_mounts(specs)
    app.extensions["lab_specs"] = specs
    app.extensions["lab_mounts"] = mounts

    @app.context_processor
    def inject_hub_nav():
        nav_mounts = [
            mount
            for mount in app.extensions.get("lab_mounts", [])
            if mount.spec.enabled and mount.app is not None
        ]
        nav_mounts = sorted(nav_mounts, key=lambda item: int(item.spec.nav_order))
        return {"hub_nav_mounts": nav_mounts}

    app.register_blueprint(hub_bp)
    app.register_blueprint(routes_compat_bp)
    return app


def create_app(config: dict | None = None):
    """Create the full WSGI application with mounted sub-lab apps."""

    hub_app = create_hub_app(config=config)
    mount_map = {}
    themed_by_slug = {}
    for mount in hub_app.extensions.get("lab_mounts", []):
        if mount.app is None or mount.error is not None:
            continue
        themed_app = LabThemeWrapper(mount.app, slug=mount.spec.slug)
        mount_map[f"/{mount.spec.slug}"] = themed_app
        themed_by_slug[mount.spec.slug] = themed_app

    # API compatibility alias for legacy RPS absolute calls (/api/v1/*).
    # This avoids browser-visible redirect HTML for JSON fetches.
    rps_app = themed_by_slug.get("rps")
    if rps_app is not None:
        mount_map["/api/v1"] = PathPrefixWrapper(rps_app, prefix="/api/v1")

    return DispatcherMiddleware(hub_app.wsgi_app, mount_map)
