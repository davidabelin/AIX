"""Lab registry contracts and mount resolution for AIX."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


LabLoader = Callable[[], Any]


@dataclass(slots=True)
class LabSpec:
    """One lab registration entry."""

    slug: str
    display_name: str
    nav_order: int
    summary: str
    loader: LabLoader
    enabled: bool = True


@dataclass(slots=True)
class LabMount:
    """Resolved mount state for one lab."""

    spec: LabSpec
    app: Any | None
    error: str | None = None


def build_lab_specs() -> list[LabSpec]:
    """Return default lab specs for the current AIX build."""

    from aix_web.labs.euclidorithm_adapter import load_euclidorithm_app
    from aix_web.labs.polyfolds_adapter import load_polyfolds_app
    from aix_web.labs.rps_adapter import load_rps_app

    return sorted(
        [
            LabSpec(
                slug="rps",
                display_name="RPS Agent Lab",
                nav_order=10,
                summary="Stable gameplay, supervised training, RL, and benchmarks.",
                loader=load_rps_app,
            ),
            LabSpec(
                slug="euclidorithm",
                display_name="Euclidorithm",
                nav_order=20,
                summary="Extended Euclidean algorithm visual and interactive lab.",
                loader=load_euclidorithm_app,
            ),
            LabSpec(
                slug="polyfolds",
                display_name="Polyfolds",
                nav_order=30,
                summary="Polyhedral net generation and dataset tooling (web shell placeholder).",
                loader=load_polyfolds_app,
            ),
        ],
        key=lambda spec: int(spec.nav_order),
    )


def resolve_lab_mounts(specs: list[LabSpec]) -> list[LabMount]:
    """Resolve all enabled labs to WSGI mounts, capturing import errors."""

    mounts: list[LabMount] = []
    for spec in specs:
        if not spec.enabled:
            mounts.append(LabMount(spec=spec, app=None, error="disabled"))
            continue
        try:
            app = spec.loader()
        except Exception as exc:  # pragma: no cover
            mounts.append(LabMount(spec=spec, app=None, error=str(exc)))
            continue
        mounts.append(LabMount(spec=spec, app=app, error=None))
    return mounts

