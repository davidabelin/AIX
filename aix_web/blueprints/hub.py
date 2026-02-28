"""Hub routes for the AIX umbrella application."""

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, render_template

hub_bp = Blueprint("hub", __name__)


def _sorted_mounts():
    mounts = current_app.extensions.get("lab_mounts", [])
    return sorted(mounts, key=lambda item: int(item.spec.nav_order))


def _mount_status(mount) -> tuple[str, str | None]:
    if mount.error == "disabled" or mount.app is None:
        return "disabled", None
    runtime_error = getattr(mount.app, "error", None)
    if runtime_error:
        return "failed", str(runtime_error)
    if bool(getattr(mount.app, "loaded", False)):
        return "mounted", None
    return "pending", None


@hub_bp.get("/")
def home() -> str:
    """Render AIX landing page with registered lab status cards."""

    cards = []
    for mount in _sorted_mounts():
        status, error = _mount_status(mount)
        cards.append(
            {
                "mount": mount,
                "status": status,
                "error": error,
            }
        )
    return render_template(
        "pages/hub.html",
        lab_cards=cards,
        title=current_app.config.get("HUB_TITLE", "AIX"),
    )


@hub_bp.get("/healthz")
def healthz():
    """Return service and mounted-lab health summary."""

    mounts = _sorted_mounts()
    configured = [m.spec.slug for m in mounts]
    mounted = []
    pending = []
    disabled = []
    failed: dict[str, str] = {}
    for mount in mounts:
        status, error = _mount_status(mount)
        slug = mount.spec.slug
        if status == "mounted":
            mounted.append(slug)
        elif status == "pending":
            pending.append(slug)
        elif status == "disabled":
            disabled.append(slug)
        elif status == "failed":
            failed[slug] = error or "unknown error"
    return jsonify(
        {
            "status": "ok",
            "service": "aix-hub",
            "timestamp": datetime.now(UTC).isoformat(),
            "configured_labs": configured,
            "mounted_labs": mounted,
            "pending_labs": pending,
            "disabled_labs": disabled,
            "failed_labs": failed,
        }
    )
