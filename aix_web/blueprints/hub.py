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
        "drl": {
            "app_url_set": _present_env("AIX_DRL_APP_URL") or _present_env("DRL_APP_URL") or _present_env("DRL_PUBLIC_URL"),
            "repo_override_set": _present_env("AIX_DRL_REPO"),
        },
        "euclidorithm": {
            "repo_override_set": _present_env("AIX_EUCLIDORITHM_REPO"),
        },
        "polyfolds": {
            "repo_override_set": _present_env("AIX_POLYFOLDS_REPO"),
            "jobs_root_override_set": _present_env("AIX_POLYFOLDS_JOBS_ROOT"),
        },
    }


def _toc_sections() -> list[dict]:
    specs = {spec.slug: spec for spec in current_app.extensions.get("lab_specs", [])}
    return [
        {
            "title": "AIX Hub",
            "summary": "Umbrella navigation, service status, and bridge diagnostics for the active AIX runtime.",
            "routes": [
                {"path": "/", "label": "Hub Home", "summary": "Primary splash page and launch surface for current AIX labs."},
                {"path": "/healthz", "label": "Health", "summary": "JSON health summary for the AIX hub and mounted labs."},
                {
                    "path": "/diagnostics/bridges",
                    "label": "Bridge Diagnostics",
                    "summary": "JSON snapshot of bridge/runtime configuration and lab mount state.",
                },
            ],
        },
        {
            "title": specs.get("rps").display_name if specs.get("rps") else "RPS Agent Lab",
            "summary": specs.get("rps").summary if specs.get("rps") else "Rock-paper-scissors gameplay, training, RL, and arena play.",
            "routes": [
                {"path": "/rps/", "label": "RPS Home", "summary": "Launch page for the RPS lab."},
                {"path": "/rps/play", "label": "Play", "summary": "Human-vs-agent gameplay with live session scoring and throw visualization."},
                {"path": "/rps/arena", "label": "Arena", "summary": "Agent-vs-agent replay and spectator view for persisted matches."},
                {"path": "/rps/training", "label": "Training", "summary": "Supervised model training, readiness, and registry management."},
                {"path": "/rps/rl", "label": "RL", "summary": "Q-learning training jobs and reinforcement-learning experiment controls."},
            ],
        },
        {
            "title": specs.get("c4").display_name if specs.get("c4") else "Connect4",
            "summary": specs.get("c4").summary if specs.get("c4") else "Connect4 gameplay, training, and arena analysis.",
            "routes": [
                {"path": "/c4/", "label": "Connect4 Home", "summary": "Launch page for the Connect4 lab."},
                {"path": "/c4/play", "label": "Play", "summary": "Human-vs-agent Connect4 with board forecasts and session tracking."},
                {"path": "/c4/arena", "label": "Arena", "summary": "Agent-vs-agent replay with recorded column-estimate overlays."},
                {"path": "/c4/training", "label": "Training", "summary": "Curated supervised training over recorded Connect4 sessions."},
                {"path": "/c4/rl", "label": "RL", "summary": "Tabular Q-learning controls and job monitoring for Connect4."},
            ],
        },
        {
            "title": specs.get("euclidorithm").display_name if specs.get("euclidorithm") else "Euclidorithm",
            "summary": specs.get("euclidorithm").summary if specs.get("euclidorithm") else "Interactive Euclidean algorithm visualizations and models.",
            "routes": [
                {"path": "/euclidorithm/", "label": "Launch", "summary": "Main Euclidorithm landing page and lab entry."},
                {"path": "/euclidorithm/table", "label": "Extended Table", "summary": "Extended Euclidean table view with Bezout coefficient progression."},
                {"path": "/euclidorithm/extended", "label": "Extended Alias", "summary": "Alias route into the extended Euclidean table workflow."},
                {"path": "/euclidorithm/wp", "label": "Word Problem Alias", "summary": "Alternate entry path that redirects into the table workflow."},
                {"path": "/euclidorithm/quick", "label": "Quick Check", "summary": "Compact walkthrough of the Euclidean reduction sequence."},
                {"path": "/euclidorithm/gear", "label": "Gear Model", "summary": "Mechanical/visual gear interpretation of Euclidean steps."},
                {"path": "/euclidorithm/lock", "label": "Lock Model", "summary": "Lock-and-key style visualization of Euclidean structure."},
            ],
        },
        {
            "title": specs.get("polyfolds").display_name if specs.get("polyfolds") else "Polyfolds",
            "summary": specs.get("polyfolds").summary if specs.get("polyfolds") else "Standalone polyhedral net classification and repair lab shell.",
            "routes": [
                {"path": "/polyfolds/", "label": "Polyfolds Home", "summary": "Standalone Polyfolds shell for the future trained-model interaction surface."},
            ],
        },
    ]


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


@hub_bp.get("/contact")
def contact_page() -> str:
    return render_template("pages/contact.html", title="Contact Us")


@hub_bp.get("/privacy")
def privacy_page() -> str:
    return render_template("pages/privacy.html", title="Privacy")


@hub_bp.get("/toc")
def toc_page() -> str:
    return render_template("pages/toc.html", title="AIX Table of Contents", toc_sections=_toc_sections())


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
