"""Helpers for bridge-style imports from sibling lab repositories.

Role
----
This module is the narrow boundary between the umbrella ``aix`` repo and the
independent sibling lab repos that still run as importable local applications
during development. The App Engine production path now prefers standalone
services for the larger labs, but local AIX development still depends on this
bridge layer for import-path discovery.

Cross-Repo Context
------------------
The same helper is used by AIX adapters for ``rps``, ``c4``, and
``euclidorithm``. ``pf`` no longer uses an import bridge in production, but the
local AIX-side Polyfolds adapter still relies on the same repository-root
conventions.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


AIX_ROOT = Path(__file__).resolve().parents[1]


def add_import_path(env_var: str, default_relative_path: str) -> Path | None:
    """Insert one sibling-repo path into ``sys.path`` when present.

    Role
    ----
    Resolve one importable lab repository location for AIX bridge adapters.
    The function first honors an explicit environment override and then falls
    back to the default sibling layout relative to the AIX repo root.

    Parameters
    ----------
    env_var : str
        Environment-variable override for the target path.
    default_relative_path : str
        Path relative to the AIX repository root.

    Returns
    -------
    pathlib.Path | None
        The resolved path that was inserted (or already present), else ``None``
        when no candidate path exists.

    Side Effects
    ------------
    Mutates ``sys.path`` by prepending the first existing candidate path.

    Used By
    -------
    ``aix_web.labs.rps_adapter``, ``aix_web.labs.c4_adapter``, and
    ``aix_web.labs.euclidorithm_adapter``.

    Notes
    -----
    This helper intentionally does not import the target package. Adapters call
    it first and then perform the actual import so load failures remain local to
    the specific mounted lab.
    """

    override = str(os.getenv(env_var, "")).strip()
    candidates = []
    if override:
        candidates.append(Path(override).expanduser())
    candidates.append((AIX_ROOT / default_relative_path).resolve())

    for candidate in candidates:
        if not candidate.exists():
            continue
        candidate_str = str(candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        return candidate
    return None
