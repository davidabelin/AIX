"""Compatibility shim for legacy Euclidorithm adapter imports."""

from __future__ import annotations

from aix_web.labs.euclidyne_adapter import load_euclidyne_app


def load_euclidorithm_app():
    """Return the Euclidyne app through the legacy adapter name."""

    return load_euclidyne_app()
