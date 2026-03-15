"""Polyfolds lab app with phased API bridge endpoints.

Role
----
Provide the AIX-side Polyfolds shell used for local development, transitional
API bridging, and diagnostics. In production, ``polyfolds`` is now a standalone
service routed by App Engine, but AIX still keeps this lightweight shell so the
umbrella repo can surface Polyfolds job orchestration locally.
"""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, current_app, jsonify, render_template, request

from aix_web.bridge import AIX_ROOT
from aix_web.labs.polyfolds_jobs import PolyfoldsJobManager


def load_polyfolds_app() -> Flask:
    """Return the AIX-local Polyfolds shell and phase-1 job bridge.

    Cross-Repo Context
    ------------------
    The deployed user-facing app lives in the sibling ``pf`` repo under
    ``pf_web``. The offline geometry/data-generation workspace lives under
    ``pf/polyfolds``. This adapter speaks only to the latter by queuing CLI jobs
    against that development workspace.
    """

    app_root = Path(__file__).resolve().parents[1]
    app = Flask(
        "aix_polyfolds",
        template_folder=str(app_root / "templates"),
        static_folder=str(app_root / "static"),
    )
    repo_override = str(os.getenv("AIX_POLYFOLDS_REPO", "")).strip()
    repo_dir = Path(repo_override).expanduser() if repo_override else (AIX_ROOT / ".." / "pf" / "polyfolds")
    jobs_root_override = str(os.getenv("AIX_POLYFOLDS_JOBS_ROOT", "")).strip()
    if jobs_root_override:
        jobs_root = Path(jobs_root_override).expanduser()
    else:
        # App Engine standard filesystem is read-only except /tmp.
        in_gae = bool(str(os.getenv("GAE_ENV", "")).strip()) or bool(str(os.getenv("K_SERVICE", "")).strip())
        jobs_root = Path("/tmp/polyfolds_jobs") if in_gae else (AIX_ROOT / "data" / "polyfolds_jobs")
    manager = PolyfoldsJobManager(
        repo_dir=repo_dir,
        jobs_root=jobs_root,
        max_workers=1,
    )
    app.extensions["polyfolds_jobs"] = manager

    def _jobs() -> PolyfoldsJobManager:
        """Return the local Polyfolds job manager extension."""

        return current_app.extensions["polyfolds_jobs"]

    @app.get("/")
    def polyfolds_home() -> str:
        """Render the AIX-side Polyfolds landing shell."""

        return render_template(
            "pages/polyfolds_home.html",
            title="Polyfolds",
        )

    @app.get("/api/v1/presets")
    def polyfolds_presets():
        """Return lightweight preset metadata for the phase-1 jobs API."""

        return jsonify(
            {
                "solids": ["tetra", "hexa", "octa", "dodeca", "icosa"],
                "kinds": ["dataset", "nets"],
                "defaults": {
                    "dataset": {
                        "quick": True,
                        "n_valid": 200,
                        "n_incomplete": 200,
                        "n_invalid": 200,
                    },
                    "nets": {
                        "count": 6,
                    },
                },
            }
        )

    @app.post("/api/v1/jobs")
    def polyfolds_create_job():
        """Validate and enqueue one Polyfolds dataset or nets job."""

        payload = request.get_json(silent=True) or {}
        try:
            job = _jobs().submit_job(payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"job": job}), 202

    @app.get("/api/v1/jobs")
    def polyfolds_list_jobs():
        """Return recent Polyfolds job records from the in-memory queue."""

        limit_raw = request.args.get("limit", "100")
        try:
            limit = max(1, min(500, int(limit_raw)))
        except ValueError:
            return jsonify({"error": "limit must be an integer."}), 400
        jobs = _jobs().list_jobs(limit=limit)
        return jsonify({"jobs": jobs})

    @app.get("/api/v1/jobs/<int:job_id>")
    def polyfolds_get_job(job_id: int):
        """Return one Polyfolds job record by id."""

        job = _jobs().get_job(job_id)
        if job is None:
            return jsonify({"error": "Job not found."}), 404
        return jsonify({"job": job})

    @app.get("/healthz")
    def polyfolds_healthz():
        """Return lightweight health details for the AIX-side Polyfolds bridge."""

        repo_exists = Path(manager.repo_dir).exists()
        return jsonify(
            {
                "status": "ok",
                "service": "polyfolds-adapter",
                "phase": "phase1-jobs",
                "repo_dir": str(manager.repo_dir),
                "repo_exists": repo_exists,
            }
        )

    return app
