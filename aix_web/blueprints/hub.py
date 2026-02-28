"""Hub routes for the AIX umbrella application."""

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, render_template

hub_bp = Blueprint("hub", __name__)


def _sorted_mounts():
    mounts = current_app.extensions.get("lab_mounts", [])
    return sorted(mounts, key=lambda item: int(item.spec.nav_order))


@hub_bp.get("/")
def home() -> str:
    """Render AIX landing page with registered lab status cards."""

    return render_template(
        "pages/hub.html",
        lab_mounts=_sorted_mounts(),
        title=current_app.config.get("HUB_TITLE", "AIX"),
    )


@hub_bp.get("/healthz")
def healthz():
    """Return service and mounted-lab health summary."""

    mounts = _sorted_mounts()
    mounted = [m.spec.slug for m in mounts if m.app is not None and m.error is None]
    failed = {
        m.spec.slug: m.error
        for m in mounts
        if m.app is None and m.error not in {None, "disabled"}
    }
    return jsonify(
        {
            "status": "ok",
            "service": "aix-hub",
            "timestamp": datetime.now(UTC).isoformat(),
            "mounted_labs": mounted,
            "failed_labs": failed,
        }
    )

