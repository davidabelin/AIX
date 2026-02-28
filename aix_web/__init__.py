"""AIX app factory and WSGI dispatcher wiring."""

from __future__ import annotations

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from aix_web.blueprints.hub import hub_bp
from aix_web.blueprints.routes_compat import routes_compat_bp
from aix_web.lab_registry import build_lab_specs, resolve_lab_mounts
from aix_web.lab_theme_wrapper import LabThemeWrapper


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
    for mount in hub_app.extensions.get("lab_mounts", []):
        if mount.app is None or mount.error is not None:
            continue
        mount_map[f"/{mount.spec.slug}"] = LabThemeWrapper(mount.app, slug=mount.spec.slug)
    return DispatcherMiddleware(hub_app.wsgi_app, mount_map)
