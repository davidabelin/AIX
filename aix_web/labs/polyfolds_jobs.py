"""Background job orchestration for bridged Polyfolds CLI commands.

Role
----
Provide the narrow runtime that lets AIX queue and execute offline Polyfolds
CLI commands against the development workspace under ``pf/polyfolds``.

Cross-Repo Context
------------------
This manager does not run the standalone ``pf_web`` service. It targets the
offline Polyfolds generators and dataset builders so AIX can offer a temporary
jobs API while the full standalone product takes shape.
"""

from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any

from aix_web.bridge import AIX_ROOT


def utcnow_iso() -> str:
    """Return a timezone-aware UTC timestamp string for job metadata."""

    return datetime.now(UTC).isoformat()


class PolyfoldsJobManager:
    """Queue and execute Polyfolds CLI jobs.

    Role
    ----
    Accept API payloads from the AIX-side Polyfolds shell, normalize them into
    concrete CLI commands, and track their lifecycle in an in-memory job table.

    Depends On
    ----------
    The offline ``pf/polyfolds`` workspace and the solid-specific CLI scripts
    it exposes.
    """

    SOLID_SCRIPT = {
        "tetra": "solid_tetra.py",
        "hexa": "solid_hexa.py",
        "octa": "solid_octa.py",
        "dodeca": "solid_dodeca.py",
        "icosa": "solid_icosa.py",
    }

    def __init__(
        self,
        *,
        repo_dir: Path,
        jobs_root: Path | None = None,
        max_workers: int = 1,
    ) -> None:
        self.repo_dir = Path(repo_dir).resolve()
        self.jobs_root = Path(jobs_root or (AIX_ROOT / "data" / "polyfolds_jobs")).resolve()
        self.logs_root = self.jobs_root / "logs"
        self.outputs_root = self.jobs_root / "outputs"
        self.logs_root.mkdir(parents=True, exist_ok=True)
        self.outputs_root.mkdir(parents=True, exist_ok=True)

        self._lock = RLock()
        self._jobs: dict[int, dict[str, Any]] = {}
        self._next_id = 0
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="polyfolds-job")

    def submit_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create and queue one Polyfolds job from API payload.

        Side Effects
        ------------
        Creates a job record, allocates output/log paths, and submits execution
        to the background thread pool.
        """

        if not self.repo_dir.exists():
            raise ValueError(
                "Polyfolds runtime repo is unavailable in this deployment. "
                f"Expected repo_dir: {self.repo_dir}"
            )

        kind = str(payload.get("kind", "dataset")).strip().lower()
        solid = str(payload.get("solid", "tetra")).strip().lower()
        params = payload.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("params must be a JSON object.")
        if kind not in {"dataset", "nets"}:
            raise ValueError("kind must be 'dataset' or 'nets'.")
        if solid not in self.SOLID_SCRIPT:
            allowed = ", ".join(sorted(self.SOLID_SCRIPT))
            raise ValueError(f"solid must be one of: {allowed}")

        with self._lock:
            self._next_id += 1
            job_id = int(self._next_id)

        command, out_dir, timeout_seconds = self._build_command(
            job_id=job_id,
            kind=kind,
            solid=solid,
            params=params,
        )
        now = utcnow_iso()
        record = {
            "id": job_id,
            "kind": kind,
            "solid": solid,
            "status": "queued",
            "params": params,
            "command": command,
            "repo_dir": str(self.repo_dir),
            "out_dir": str(out_dir),
            "timeout_seconds": timeout_seconds,
            "stdout_log": str(self.logs_root / f"job_{job_id:05d}.stdout.log"),
            "stderr_log": str(self.logs_root / f"job_{job_id:05d}.stderr.log"),
            "exit_code": None,
            "error_message": None,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "finished_at": None,
        }
        with self._lock:
            self._jobs[job_id] = record
        self._executor.submit(self._run_job, job_id)
        return self.get_job(job_id) or record

    def list_jobs(self, *, limit: int = 100) -> list[dict[str, Any]]:
        """Return recent jobs ordered by descending id."""

        with self._lock:
            rows = list(self._jobs.values())
        rows.sort(key=lambda row: int(row["id"]), reverse=True)
        return [dict(row) for row in rows[: max(1, int(limit))]]

    def get_job(self, job_id: int) -> dict[str, Any] | None:
        """Return one job by id."""

        with self._lock:
            row = self._jobs.get(int(job_id))
        return dict(row) if row else None

    def _update_job(self, job_id: int, **updates: Any) -> None:
        """Apply an in-place mutation to one tracked job record."""

        with self._lock:
            row = self._jobs.get(int(job_id))
            if row is None:
                return
            row.update(updates)
            row["updated_at"] = utcnow_iso()

    def _build_command(
        self,
        *,
        job_id: int,
        kind: str,
        solid: str,
        params: dict[str, Any],
    ) -> tuple[list[str], Path, int]:
        """Translate one normalized job payload into a concrete CLI command.

        Returns
        -------
        tuple[list[str], pathlib.Path, int]
            The command argv, output directory, and bounded timeout in seconds.
        """

        script = self.SOLID_SCRIPT[solid]
        out_dir = params.get("out_dir")
        if out_dir:
            output_path = Path(str(out_dir)).expanduser()
            if not output_path.is_absolute():
                output_path = (AIX_ROOT / output_path).resolve()
        else:
            output_path = (self.outputs_root / f"{solid}_{kind}_job_{job_id:05d}").resolve()

        command = [sys.executable, script, kind, "--out-dir", str(output_path)]
        command += self._optional_flag("--seed", params.get("seed"), int)
        command += self._optional_flag("--img-size", params.get("img_size"), int)
        command += self._optional_flag("--palette", params.get("palette"), str)
        command += self._optional_flag("--line-width", params.get("line_width"), float)
        command += self._optional_flag("--workers", params.get("workers"), int)
        command += self._optional_flag("--chunksize", params.get("chunksize"), int)

        if kind == "dataset":
            command += self._optional_flag("--n-valid", params.get("n_valid", 200), int)
            command += self._optional_flag("--n-incomplete", params.get("n_incomplete", 200), int)
            command += self._optional_flag("--n-invalid", params.get("n_invalid", 200), int)
            command += self._optional_flag("--sidelength", params.get("sidelength"), float)
            command += self._optional_flag("--max-tries", params.get("max_tries"), int)
            command += self._optional_flag("--missing", params.get("missing"), int)
            if bool(params.get("quick", True)):
                command.append("--test")
            if bool(params.get("plot", False)):
                command.append("--plot")
            if bool(params.get("fast", False)):
                command.append("--fast")
        else:
            command += self._optional_flag("--count", params.get("count", 6), int)
            command += self._optional_flag("--sidelength", params.get("sidelength"), float)
            command += self._optional_flag("--max-tries", params.get("max_tries"), int)
            if bool(params.get("labels", False)):
                command.append("--labels")
            if bool(params.get("no_png", False)):
                command.append("--no-png")
            if bool(params.get("fast", False)):
                command.append("--fast")

        timeout_seconds = int(params.get("timeout_seconds", 900))
        timeout_seconds = max(30, min(timeout_seconds, 3600))
        return command, output_path, timeout_seconds

    @staticmethod
    def _optional_flag(name: str, value: Any, cast) -> list[str]:
        """Return one CLI flag pair when a value is present."""

        if value is None:
            return []
        return [name, str(cast(value))]

    def _run_job(self, job_id: int) -> None:
        """Execute one queued job and persist terminal status metadata."""

        row = self.get_job(job_id)
        if row is None:
            return
        self._update_job(job_id, status="running", started_at=utcnow_iso())

        stdout_log = Path(row["stdout_log"])
        stderr_log = Path(row["stderr_log"])
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stderr_log.parent.mkdir(parents=True, exist_ok=True)

        try:
            proc = subprocess.run(
                row["command"],
                cwd=row["repo_dir"],
                capture_output=True,
                text=True,
                timeout=int(row["timeout_seconds"]),
                check=False,
            )
            stdout_log.write_text(proc.stdout or "", encoding="utf-8")
            stderr_log.write_text(proc.stderr or "", encoding="utf-8")
            if int(proc.returncode) == 0:
                self._update_job(
                    job_id,
                    status="completed",
                    exit_code=int(proc.returncode),
                    finished_at=utcnow_iso(),
                    error_message=None,
                )
                return
            message = (proc.stderr or proc.stdout or "").strip()
            message = message[:400] if message else f"process exited with code {proc.returncode}"
            self._update_job(
                job_id,
                status="failed",
                exit_code=int(proc.returncode),
                finished_at=utcnow_iso(),
                error_message=message,
            )
        except subprocess.TimeoutExpired as exc:
            stdout_log.write_text((exc.stdout or ""), encoding="utf-8")
            stderr_log.write_text((exc.stderr or ""), encoding="utf-8")
            self._update_job(
                job_id,
                status="failed",
                exit_code=None,
                finished_at=utcnow_iso(),
                error_message=f"job timed out after {row['timeout_seconds']} seconds",
            )
        except Exception as exc:  # pragma: no cover
            self._update_job(
                job_id,
                status="failed",
                exit_code=None,
                finished_at=utcnow_iso(),
                error_message=str(exc),
            )
