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


def _build_injection(slug: str) -> str:
    palette = LAB_PALETTES.get(slug, LAB_PALETTES["rps"])
    return f"""
<style id="aix-arm-theme">
  :root {{
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
  }}
  h1, h2, h3 {{
    font-family: "Baskervville", Georgia, serif;
    font-weight: 400;
  }}
  #aix-subpage-back {{
    position: fixed;
    right: 16px;
    bottom: 14px;
    z-index: 9999;
    text-decoration: none;
    color: #fff;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border-radius: 999px;
    padding: 9px 12px;
    font-size: 0.88rem;
    font-weight: 600;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.16);
  }}
  #aix-subpage-back:hover {{
    filter: brightness(1.04);
  }}
</style>
<a id="aix-subpage-back" href="/">Back to AIX Hub</a>
""".strip()


def _inject_html(html_text: str, slug: str) -> str:
    if 'id="aix-subpage-back"' in html_text:
        return html_text
    snippet = _build_injection(slug)
    if _BODY_CLOSE_RE.search(html_text):
        return _BODY_CLOSE_RE.sub(f"{snippet}</body>", html_text, count=1)
    return html_text + snippet


def _header_value(headers, name: str) -> str:
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
