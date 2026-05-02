"""HTML response wrapper for shared lab chrome and per-lab palettes."""

from __future__ import annotations

import re


LAB_PALETTES = {
    "rps": {
        "accent": "#0f7b6d",
        "accent_2": "#ff6f3c",
        "paper": "#fff8ef",
        "panel": "#fffdf9",
        "line": "#dfd8ce",
        "muted": "#615f67",
        "brand": "#0f7b6d",
        "brand_soft": "#dff3ee",
        "bg": "#f4f8f7",
        "bg_alt": "#eef5f3",
    },
    "c4": {
        "accent": "#8a1f2f",
        "accent_2": "#f08d2e",
        "paper": "#fff7f4",
        "panel": "#fffdfa",
        "line": "#e2d4cf",
        "muted": "#695962",
        "brand": "#8a1f2f",
        "brand_soft": "#f8dfe4",
        "bg": "#faf3f1",
        "bg_alt": "#f3e9e6",
    },
    "clue": {
        "accent": "#9f2f31",
        "accent_2": "#d0a465",
        "paper": "#f8f0df",
        "panel": "#fffaf1",
        "line": "#d8c5a8",
        "muted": "#66594c",
        "brand": "#9f2f31",
        "brand_soft": "#f3ddd0",
        "bg": "#f2ead8",
        "bg_alt": "#ebe2cb",
    },
    "doubledigits": {
        "accent": "#9e5125",
        "accent_2": "#1f6f78",
        "paper": "#fcf6ef",
        "panel": "#fffdf9",
        "line": "#dfd4c5",
        "muted": "#665b52",
        "brand": "#9e5125",
        "brand_soft": "#f4e1d0",
        "bg": "#f8f4ee",
        "bg_alt": "#eef5f4",
    },
    "drl": {
        "accent": "#9a4d1a",
        "accent_2": "#1f7a75",
        "paper": "#fdf8f2",
        "panel": "#fffdfa",
        "line": "#e4d6cb",
        "muted": "#6c5d56",
        "brand": "#9a4d1a",
        "brand_soft": "#f7e6d8",
        "bg": "#faf5ef",
        "bg_alt": "#eef6f5",
    },
    "euclidyne": {
        "accent": "#0a4f8b",
        "accent_2": "#b66d2f",
        "paper": "#f4f7fb",
        "panel": "#ffffff",
        "line": "#cad5e3",
        "muted": "#4e5a67",
        "brand": "#0a4f8b",
        "brand_soft": "#dbe9f8",
        "bg": "#f4f7fb",
        "bg_alt": "#eef3fa",
    },
    "euclidorithm": {
        "accent": "#0a4f8b",
        "accent_2": "#b66d2f",
        "paper": "#f4f7fb",
        "panel": "#ffffff",
        "line": "#cad5e3",
        "muted": "#4e5a67",
        "brand": "#0a4f8b",
        "brand_soft": "#dbe9f8",
        "bg": "#f4f7fb",
        "bg_alt": "#eef3fa",
    },
    "polyfolds": {
        "accent": "#2f7d32",
        "accent_2": "#c7771f",
        "paper": "#faf8ef",
        "panel": "#fffef9",
        "line": "#ddd8c8",
        "muted": "#626055",
        "brand": "#2f7d32",
        "brand_soft": "#e3f0e1",
        "bg": "#f6f8f1",
        "bg_alt": "#eef3e7",
    },
}


_BODY_CLOSE_RE = re.compile(r"</body\s*>", re.IGNORECASE)
_BACK_LABEL_RE = re.compile(r">Back to AIX Hub<")
_FOOTER_COPY_RE = re.compile(
    r'<p class="footer-copy[^"]*">.*?2026 AIX Protodyne.*?</p>',
    re.IGNORECASE | re.DOTALL,
)


def _build_injection(slug: str) -> str:
    """Build the CSS and back-link snippet injected into lab HTML responses."""

    palette = LAB_PALETTES.get(slug, LAB_PALETTES["rps"])
    compact = slug != "clue"
    body_font_size = "0.86rem" if compact else "initial"
    header_gap = "0.55rem" if compact else "0.8rem"
    header_padding = "0.66rem clamp(0.7rem, 2vw, 1.35rem)" if compact else "1rem clamp(0.9rem, 3vw, 1.6rem)"
    nav_gap = "0.42rem" if compact else "0.7rem"
    main_width = "min(900px, 94vw)" if compact else "min(1020px, 94vw)"
    main_margin = "0.8rem auto 1.35rem" if compact else "1.15rem auto 2rem"
    main_gap = "0.62rem" if compact else "0.9rem"
    panel_radius = "10px" if compact else "14px"
    panel_padding = "0.62rem 0.72rem" if compact else "0.95rem 1.05rem"
    panel_shadow = "0 7px 18px rgba(16, 12, 9, 0.07)" if compact else "0 8px 24px rgba(16, 12, 9, 0.08)"
    back_right = "12px" if compact else "16px"
    back_bottom = "11px" if compact else "14px"
    back_padding = "7px 10px" if compact else "9px 12px"
    back_font_size = "0.78rem" if compact else "0.88rem"
    compact_overrides = (
        """
  body {
    overflow-x: hidden;
  }
  main, .page {
    max-width: calc(100vw - 0.8rem);
    min-width: 0;
  }
  section, .panel, .card {
    max-width: 100%;
    min-width: 0;
    overflow-wrap: anywhere;
  }
  input, select, button, textarea {
    max-width: 100%;
  }
  @media (max-width: 700px) {
    main, .page {
      width: calc(100vw - 0.8rem);
    }
    section, .panel, .card {
      overflow-x: auto;
    }
  }
"""
        if compact
        else ""
    )
    return f"""
<style id="aix-arm-theme">
  :root {{
    --ink: #1f1f24;
    --accent: {palette["accent"]};
    --accent-2: {palette["accent_2"]};
    --paper: {palette["paper"]};
    --panel: {palette["panel"]};
    --line: {palette["line"]};
    --muted: {palette["muted"]};
    --brand: {palette["brand"]};
    --brand-soft: {palette["brand_soft"]};
    --bg: {palette["bg"]};
    --bg-alt: {palette["bg_alt"]};
    --card: {palette["panel"]};
    --border: {palette["line"]};
  }}
  body {{
    font-family: "Space Grotesk", "Segoe UI", sans-serif;
    font-size: {body_font_size};
    color: var(--ink, #1f1f24);
    background:
      radial-gradient(circle at 20% 10%, var(--brand-soft) 0%, transparent 40%),
      radial-gradient(circle at 80% 20%, var(--bg) 0%, transparent 35%),
      linear-gradient(160deg, var(--paper), var(--bg-alt));
  }}
  h1, h2, h3 {{
    font-family: "Baskervville", Georgia, serif;
    font-weight: 400;
  }}
  header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: {header_gap};
    padding: {header_padding};
    background: var(--paper);
    border-bottom: 1px solid var(--line);
  }}
  nav {{
    display: flex;
    gap: {nav_gap};
    flex-wrap: wrap;
  }}
  main {{
    width: {main_width};
    margin: {main_margin};
    display: grid;
    gap: {main_gap};
  }}
  section, .panel, .card {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: {panel_radius};
    padding: {panel_padding};
    box-shadow: {panel_shadow};
  }}
  a {{
    color: var(--brand);
  }}
  button, input, select, .btn {{
    font: inherit;
  }}
  code {{
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.08rem 0.35rem;
  }}
  #aix-subpage-back {{
    position: fixed;
    right: {back_right};
    bottom: {back_bottom};
    z-index: 9999;
    text-decoration: none;
    color: #fff;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border-radius: 999px;
    padding: {back_padding};
    font-size: {back_font_size};
    font-weight: 600;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.16);
  }}
  #aix-subpage-back:hover {{
    filter: brightness(1.04);
  }}
  .aix-footer-copy {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
  }}
  .aix-footer-copy .copyleft-mark {{
    width: 16px;
    height: 16px;
    max-width: 16px;
    max-height: 16px;
    flex: 0 0 auto;
  }}
{compact_overrides}
</style>
<a id="aix-subpage-back" href="/">AIX Labs</a>
""".strip()


def _normalize_aix_chrome(html_text: str) -> str:
    """Rewrite shared AIX chrome labels/footers across mounted lab HTML."""

    html_text = _BACK_LABEL_RE.sub(">AIX Labs<", html_text)
    footer_markup = (
        '<p class="footer-copy aix-footer-copy">'
        '<img class="copyleft-mark" src="/static/icons/copyleft.svg" alt="" aria-hidden="true" width="16" height="16">'
        "<span>2026 AIX Protodyne</span>"
        "</p>"
    )
    html_text = _FOOTER_COPY_RE.sub(footer_markup, html_text)
    return html_text


def _inject_html(html_text: str, slug: str) -> str:
    """Inject shared AIX chrome into one HTML document when absent."""

    html_text = _normalize_aix_chrome(html_text)
    if 'id="aix-subpage-back"' in html_text:
        return html_text
    snippet = _build_injection(slug)
    if _BODY_CLOSE_RE.search(html_text):
        return _BODY_CLOSE_RE.sub(f"{snippet}</body>", html_text, count=1)
    return html_text + snippet


def _header_value(headers, name: str) -> str:
    """Return one header value from a WSGI-style header list."""

    for key, value in headers:
        if str(key).lower() == str(name).lower():
            return str(value)
    return ""


class LabThemeWrapper:
    """Wrap one mounted lab app to inject AIX chrome into HTML responses."""

    def __init__(self, app, *, slug: str) -> None:
        self._app = app
        self.slug = str(slug)

    @property
    def loaded(self) -> bool:
        return bool(getattr(self._app, "loaded", False))

    @property
    def error(self) -> str | None:
        return getattr(self._app, "error", None)

    def __call__(self, environ, start_response):
        """Dispatch one request and inject AIX chrome into HTML responses."""

        captured = {}

        def _capture_start_response(status, headers, exc_info=None):
            captured["status"] = status
            captured["headers"] = list(headers)
            captured["exc_info"] = exc_info
            return lambda _chunk: None

        app_iter = self._app(environ, _capture_start_response)
        headers = captured.get("headers", [])
        content_type = _header_value(headers, "Content-Type").lower()
        if "text/html" not in content_type:
            start_response(captured.get("status", "200 OK"), headers, captured.get("exc_info"))
            return app_iter

        try:
            body = b"".join(app_iter)
        finally:
            if hasattr(app_iter, "close"):
                app_iter.close()
        text = body.decode("utf-8", errors="replace")
        patched = _inject_html(text, self.slug).encode("utf-8")

        response_headers = [
            (k, v)
            for (k, v) in headers
            if str(k).lower() not in {"content-length", "content-encoding", "etag"}
        ]
        response_headers.append(("Content-Length", str(len(patched))))
        start_response(captured.get("status", "200 OK"), response_headers, captured.get("exc_info"))
        return [patched]
