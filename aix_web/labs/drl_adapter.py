"""AIX-native portal app for the separate DRL sister web application.

Role
----
Expose DRL inside AIX as a sister-app portal rather than an in-process mount.
This preserves one coherent AIX navigation surface without forcing the DRL app
to share the AIX runtime or deployment model.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

from flask import Flask, jsonify, render_template


AIX_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class DrlLink:
    """One curated DRL route surfaced in the AIX sister-app portal."""

    label: str
    path: str
    summary: str
    group: str
    thumbnail: str


DRL_LINKS: tuple[DrlLink, ...] = (
    DrlLink("Overview", "/", "Main landing page for the DRL sister app.", "Core", "overview"),
    DrlLink("Inventory", "/inventory", "Repository-wide inventory and recovery map.", "Core", "inventory"),
    DrlLink("Foundations Demo", "/demos/foundations", "Interactive warm-up demo for the foundational RL arm.", "Interactive", "demo-foundations"),
    DrlLink("Finance Demo", "/demos/finance", "Interactive finance execution demo.", "Interactive", "demo-finance"),
    DrlLink("Lunar Lander", "/lunar", "Live Lunar runtime, checkpoints, and training jobs.", "Interactive", "lunar"),
    DrlLink("Foundations", "/sections/foundations", "Tabular RL, dynamic programming, MC, TD, and early labs.", "Arms", "foundations"),
    DrlLink("Value-Based", "/sections/value-based", "DQN lineage, navigation, and Lunar variants.", "Arms", "value-based"),
    DrlLink("Policy Gradients", "/sections/policy-gradients", "REINFORCE, PPO, actor-critic, and Pong-era material.", "Arms", "policy"),
    DrlLink("Continuous Control", "/sections/continuous-control", "Reacher, DDPG, and Unity-heavy recovery work.", "Arms", "continuous"),
    DrlLink("Multi-Agent", "/sections/multi-agent", "Tennis, Soccer, MARL notes, and theory material.", "Arms", "multi-agent"),
    DrlLink("Finance", "/sections/finance", "Domain application branch for RL-guided execution.", "Arms", "finance"),
    DrlLink("Papers", "/sections/papers", "Reference shelf for the educational side of DRL.", "Archive", "papers"),
    DrlLink("Archive", "/sections/archive", "Legacy branches kept visible but not yet productized.", "Archive", "archive"),
)


def _normalized_external_url() -> str:
    """Resolve the externally reachable DRL base URL from environment hints.

    Used By
    -------
    The DRL portal context builder, so launch links can point at the deployed
    sister app when available.
    """

    for key in ("AIX_DRL_APP_URL", "DRL_APP_URL", "DRL_PUBLIC_URL"):
        value = str(os.getenv(key, "")).strip()
        if value:
            return value.rstrip("/")
    return ""


def _repo_root() -> Path:
    """Resolve the local DRL repository root for diagnostics only."""

    override = str(os.getenv("AIX_DRL_REPO", "")).strip()
    if override:
        return Path(override).expanduser().resolve()
    return (AIX_ROOT / ".." / "drl").resolve()


def _build_context() -> dict:
    """Build the render context for the AIX DRL portal page.

    Role
    ----
    Translate the static curated link catalog into grouped launch rows and
    diagnostics that the AIX hub can present without importing the DRL app.
    """

    external_url = _normalized_external_url()
    repo_root = _repo_root()
    grouped: dict[str, list[dict]] = {}
    for item in DRL_LINKS:
        grouped.setdefault(item.group, []).append(
            {
                "label": item.label,
                "path": item.path,
                "summary": item.summary,
                "thumbnail": item.thumbnail,
                "url": (urljoin(f"{external_url}/", item.path.lstrip("/")) if external_url else None),
            }
        )
    return {
        "external_url": external_url or None,
        "repo_root": str(repo_root),
        "repo_present": repo_root.exists(),
        "toc_groups": grouped,
        "quick_links": [
            {
                "label": "Open DRL Sister App",
                "url": external_url,
                "enabled": bool(external_url),
            },
            {
                "label": "Lunar Lander",
                "url": (urljoin(f"{external_url}/", "lunar") if external_url else None),
                "enabled": bool(external_url),
            },
            {
                "label": "Inventory",
                "url": (urljoin(f"{external_url}/", "inventory") if external_url else None),
                "enabled": bool(external_url),
            },
        ],
    }


def load_drl_app() -> Flask:
    """Return the AIX-local DRL portal app.

    Cross-Repo Context
    ------------------
    Unlike ``rps`` and ``c4``, this does not bridge directly into the sibling
    DRL Flask application. It creates a small AIX-owned Flask app that points
    outward to the standalone DRL deployment and local repo metadata.
    """

    app = Flask(
        "aix_drl_portal",
        template_folder=str(AIX_ROOT / "aix_web" / "templates"),
        static_folder=str(AIX_ROOT / "aix_web" / "static"),
    )

    @app.get("/")
    def drl_home() -> str:
        return render_template("pages/drl_portal.html", **_build_context())

    @app.get("/healthz")
    def drl_healthz():
        context = _build_context()
        return jsonify(
            {
                "status": "ok",
                "service": "aix-drl-portal",
                "external_url": context["external_url"],
                "repo_present": bool(context["repo_present"]),
                "repo_root": context["repo_root"],
            }
        )

    return app
