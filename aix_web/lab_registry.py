"""Lab registry contracts and mount resolution for AIX.

Role
----
Define the canonical list of labs the AIX hub knows about, including their
display metadata, lazy loader entrypoints, and environment-controlled
enablement.

Cross-Repo Context
------------------
This registry is where the umbrella app's understanding of the broader AIX
system becomes concrete. It references sibling repos such as ``rps`` and
``c4``, the standalone ``pf`` Polyfolds service, the AIX-local DRL portal, and
the Euclidorithm app that still lives under the geometry workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Callable

from aix_web.lazy_mount import LazyMountApp


LabLoader = Callable[[], Any]


@dataclass(slots=True)
class LabSpec:
    """One declarative lab registration entry.

    ``LabSpec`` is the stable metadata contract shared by the AIX hub UI, the
    WSGI mount builder, and diagnostics pages.
    """

    slug: str
    display_name: str
    nav_order: int
    summary: str
    loader: LabLoader
    enabled: bool = True


@dataclass(slots=True)
class LabMount:
    """Resolved mount state for one lab.

    Role
    ----
    Pair one ``LabSpec`` with its runtime mount object or an enable/load error
    marker after registry resolution.
    """

    spec: LabSpec
    app: Any | None
    error: str | None = None


def _enabled_labs_from_env(default_slugs: list[str]) -> set[str]:
    """Resolve enabled lab slugs from ``AIX_ENABLED_LABS`` when provided.

    Notes
    -----
    The environment variable acts as a production-safety valve so AIX can hide
    labs whose standalone services are not deployed or whose bridge runtime is
    intentionally unavailable.
    """

    raw = str(os.getenv("AIX_ENABLED_LABS", "")).strip()
    if not raw:
        return set(default_slugs)
    enabled = {token.strip().lower() for token in raw.split(",") if token.strip()}
    return enabled or set(default_slugs)


def build_lab_specs() -> list[LabSpec]:
    """Return default lab specs for the current AIX build.

    Role
    ----
    Construct the canonical ordered lab catalog used by the AIX hub.

    Cross-Repo Context
    ------------------
    The returned entries deliberately mix multiple integration modes:

    - ``rps`` and ``c4`` are sibling repos with their own Flask apps.
    - ``drl`` is surfaced through an AIX-native portal rather than an in-process
      mount of the DRL app itself.
    - ``euclidorithm`` is imported from the geometry workspace.
    - ``polyfolds`` is conceptually a standalone sister service even though AIX
      also retains a local fallback shell for development and diagnostics.
    """

    from aix_web.labs.c4_adapter import load_c4_app
    from aix_web.labs.drl_adapter import load_drl_app
    from aix_web.labs.euclidorithm_adapter import load_euclidorithm_app
    from aix_web.labs.polyfolds_adapter import load_polyfolds_app
    from aix_web.labs.rps_adapter import load_rps_app

    default_order = ["rps", "drl", "c4", "euclidorithm", "polyfolds"]
    enabled_slugs = _enabled_labs_from_env(default_order)

    return sorted(
        [
            LabSpec(
                slug="rps",
                display_name="RPS Agent Lab",
                nav_order=10,
                summary="Stable gameplay, supervised training, RL, and benchmarks.",
                loader=load_rps_app,
                enabled=("rps" in enabled_slugs),
            ),
            LabSpec(
                slug="drl",
                display_name="Deep RL Lab",
                nav_order=12,
                summary="AIX portal for the separate DRL sister app: TOC, orientation, and launch links.",
                loader=load_drl_app,
                enabled=("drl" in enabled_slugs),
            ),
            LabSpec(
                slug="c4",
                display_name="Connect4",
                nav_order=15,
                summary="Connect4 gameplay, supervised training, and RL experiments.",
                loader=load_c4_app,
                enabled=("c4" in enabled_slugs),
            ),
            LabSpec(
                slug="euclidorithm",
                display_name="Euclidorithm",
                nav_order=20,
                summary="Extended Euclidean algorithm visual and interactive lab.",
                loader=load_euclidorithm_app,
                enabled=("euclidorithm" in enabled_slugs),
            ),
            LabSpec(
                slug="polyfolds",
                display_name="Polyfolds",
                nav_order=30,
                summary="Standalone polyhedral net classification and repair lab.",
                loader=load_polyfolds_app,
                enabled=("polyfolds" in enabled_slugs),
            ),
        ],
        key=lambda spec: int(spec.nav_order),
    )


def resolve_lab_mounts(specs: list[LabSpec]) -> list[LabMount]:
    """Build lazy WSGI mounts for all enabled labs.

    Role
    ----
    Convert declarative ``LabSpec`` entries into runtime mount objects that the
    AIX dispatcher can attach under ``/<slug>``.

    Depends On
    ----------
    ``LazyMountApp`` for deferred import and initialization behavior.
    """

    mounts: list[LabMount] = []
    for spec in specs:
        if not spec.enabled:
            mounts.append(LabMount(spec=spec, app=None, error="disabled"))
            continue
        app = LazyMountApp(name=spec.slug, loader=spec.loader)
        mounts.append(LabMount(spec=spec, app=app, error=None))
    return mounts
