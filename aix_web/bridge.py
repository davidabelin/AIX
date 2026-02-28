"""Helpers for bridge-style imports from sibling lab repositories."""

from __future__ import annotations

import os
import sys
from pathlib import Path


AIX_ROOT = Path(__file__).resolve().parents[1]


def add_import_path(env_var: str, default_relative_path: str) -> Path | None:
    """Insert one repository path into ``sys.path`` when present.

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

