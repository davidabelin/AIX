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
the Euclidyne app that lives under the geometry workspace.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Callable

from aix_web.lazy_mount import LazyMountApp


LabLoader = Callable[[], Any]
SLUG_ALIASES = {
    "euclidorithm": "euclidyne",
}
DEFAULT_DISPATCH_SERVICE_SLUGS = {"rps", "c4", "clue", "doubledigits", "euclidyne", "polyfolds"}


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
    enabled = {
        SLUG_ALIASES.get(token.strip().lower(), token.strip().lower())
        for token in raw.split(",")
        if token.strip()
    }
    return enabled or set(default_slugs)


def _is_cloud_runtime() -> bool:
    """Return whether the hub is running in a managed cloud service."""

    return bool(str(os.getenv("GAE_ENV", "")).strip()) or bool(str(os.getenv("K_SERVICE", "")).strip())


def _dispatch_service_slugs() -> set[str]:
    """Return lab slugs served by App Engine dispatch rather than local imports."""

    raw = str(os.getenv("AIX_DISPATCH_SERVICE_LABS", "")).strip()
    if raw:
        return {
            SLUG_ALIASES.get(token.strip().lower(), token.strip().lower())
            for token in raw.split(",")
            if token.strip()
        }
    if _is_cloud_runtime():
        return set(DEFAULT_DISPATCH_SERVICE_SLUGS)
    return set()


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
    - ``euclidyne`` is imported from the geometry workspace.
    - ``polyfolds`` is conceptually a standalone sister service even though AIX
      also retains a local fallback shell for development and diagnostics.
    """

    from aix_web.labs.c4_adapter import load_c4_app
    from aix_web.labs.clue_adapter import load_clue_app
    from aix_web.labs.doubledigits_adapter import load_doubledigits_app
    from aix_web.labs.drl_adapter import load_drl_app
    from aix_web.labs.euclidyne_adapter import load_euclidyne_app
    from aix_web.labs.polyfolds_adapter import load_polyfolds_app
    from aix_web.labs.rps_adapter import load_rps_app

    default_order = ["rps", "drl", "c4", "clue", "doubledigits", "euclidyne", "polyfolds"]
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
                slug="clue",
                display_name="Clue",
                nav_order=17,
                summary="Classic Clue board play with filtered private state, public discussion, and mixed human/AI seats.",
                loader=load_clue_app,
                enabled=("clue" in enabled_slugs),
            ),
            LabSpec(
                slug="doubledigits",
                display_name="Double-digits",
                nav_order=18,
                summary="Guided handwritten-digit lab from single digits to two-digit composition and arithmetic scenes.",
                loader=load_doubledigits_app,
                enabled=("doubledigits" in enabled_slugs),
            ),
            LabSpec(
                slug="euclidyne",
                display_name="Euclidyne",
                nav_order=20,
                summary="Instrument-lab explorations into Euclid, ratios, and rhythm.",
                loader=load_euclidyne_app,
                enabled=("euclidyne" in enabled_slugs),
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
    dispatch_service_slugs = _dispatch_service_slugs()
    for spec in specs:
        if not spec.enabled:
            mounts.append(LabMount(spec=spec, app=None, error="disabled"))
            continue
        if spec.slug in dispatch_service_slugs:
            mounts.append(LabMount(spec=spec, app=None, error="deployed-service"))
            continue
        app = LazyMountApp(name=spec.slug, loader=spec.loader)
        mounts.append(LabMount(spec=spec, app=app, error=None))
    return mounts
