"""Hub routes for the AIX umbrella application."""

from __future__ import annotations

from datetime import UTC, datetime
import os

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


def _is_cloud_runtime() -> bool:
    return bool(str(os.getenv("GAE_ENV", "")).strip()) or bool(str(os.getenv("K_SERVICE", "")).strip())


def _present_env(key: str) -> bool:
    return bool(str(os.getenv(key, "")).strip())


def _runtime_warnings() -> list[str]:
    warnings: list[str] = []
    if not _is_cloud_runtime():
        return warnings
    if not (_present_env("RPS_DATABASE_URL") or _present_env("RPS_DATABASE_URL_SECRET")):
        warnings.append(
            "RPS persistence is not configured (set RPS_DATABASE_URL or RPS_DATABASE_URL_SECRET). "
            "Cloud instance restarts can lose local SQLite data."
        )
    if not (_present_env("C4_DATABASE_URL") or _present_env("C4_DATABASE_URL_SECRET")):
        warnings.append(
            "C4 persistence is not configured (set C4_DATABASE_URL or C4_DATABASE_URL_SECRET). "
            "Cloud instance restarts can lose local SQLite data."
        )
    return warnings


def _bridge_config_snapshot() -> dict:
    return {
        "runtime": {
            "is_cloud_runtime": _is_cloud_runtime(),
            "service": str(os.getenv("K_SERVICE", "")).strip(),
            "version": str(os.getenv("K_REVISION", "")).strip(),
            "project_id": str(os.getenv("GOOGLE_CLOUD_PROJECT", "")).strip(),
        },
        "rps": {
            "repo_override_set": _present_env("AIX_RPS_REPO"),
            "database_url_set": _present_env("RPS_DATABASE_URL"),
            "database_url_secret_set": _present_env("RPS_DATABASE_URL_SECRET"),
            "db_path_set": _present_env("RPS_DB_PATH"),
            "events_dir_set": _present_env("RPS_EVENTS_DIR"),
            "models_dir_set": _present_env("RPS_MODELS_DIR"),
            "exports_dir_set": _present_env("RPS_EXPORTS_DIR"),
        },
        "c4": {
            "repo_override_set": _present_env("AIX_C4_REPO"),
            "database_url_set": _present_env("C4_DATABASE_URL"),
            "database_url_secret_set": _present_env("C4_DATABASE_URL_SECRET"),
            "db_path_set": _present_env("C4_DB_PATH"),
            "events_dir_set": _present_env("C4_EVENTS_DIR"),
            "models_dir_set": _present_env("C4_MODELS_DIR"),
            "exports_dir_set": _present_env("C4_EXPORTS_DIR"),
        },
        "euclidorithm": {
            "repo_override_set": _present_env("AIX_EUCLIDORITHM_REPO"),
        },
        "polyfolds": {
            "repo_override_set": _present_env("AIX_POLYFOLDS_REPO"),
            "jobs_root_override_set": _present_env("AIX_POLYFOLDS_JOBS_ROOT"),
        },
    }


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
            "runtime_warnings": _runtime_warnings(),
        }
    )


@hub_bp.get("/diagnostics/bridges")
def bridge_diagnostics():
    """Return mount status plus non-secret bridge configuration hints."""

    mounts = _sorted_mounts()
    by_lab = {}
    for mount in mounts:
        status, error = _mount_status(mount)
        by_lab[mount.spec.slug] = {
            "status": status,
            "error": error,
            "loaded": bool(getattr(mount.app, "loaded", False)) if mount.app is not None else False,
        }
    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.now(UTC).isoformat(),
            "runtime_warnings": _runtime_warnings(),
            "bridge_config": _bridge_config_snapshot(),
            "labs": by_lab,
        }
    )
