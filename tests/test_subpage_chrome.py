from __future__ import annotations

from werkzeug.test import Client
from werkzeug.wrappers import Response

from aix_web import create_app


def test_polyfolds_page_includes_global_back_link():
    app = create_app({"TESTING": True})
    client = Client(app, Response)
    response = client.get("/polyfolds/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="aix-subpage-back"' in html
    assert "AIX Labs" in html
    assert "copyleft.svg" in html
    assert "2026 AIX Protodyne" in html
    assert "Contact Us" in html
    assert "Privacy" in html
    assert "AIX TOC" in html


def test_all_lab_home_pages_include_global_back_link():
    app = create_app({"TESTING": True})
    client = Client(app, Response)
    palette_by_path = {
        "/rps/": "#0f7b6d",
        "/drl/": "#9a4d1a",
        "/c4/": "#8a1f2f",
        "/doubledigits/": "#9e5125",
        "/euclidyne/": "#0a4f8b",
        "/polyfolds/": "#2f7d32",
    }
    for path, accent in palette_by_path.items():
        response = client.get(path)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'id="aix-subpage-back"' in html
        assert "AIX Labs" in html
        assert "copyleft.svg" in html
        assert "2026 AIX Protodyne" in html
        assert "Contact Us" in html
        assert "Privacy" in html
        assert "AIX TOC" in html
        assert f"--accent: {accent}" in html


def test_lab_footer_is_merged_instead_of_duplicated():
    from aix_web.lab_theme_wrapper import _inject_html

    lab_html = (
        "<html><body><main>Lab</main>"
        "<footer class=\"site-footer\"><div class=\"footer-inner\">"
        "<p class=\"footer-copy\"><img class=\"copyleft-mark\" src=\"/rps/static/icons/copyleft.svg\" alt=\"\">"
        "<span>2026 RPS Agent Lab</span></p>"
        "<nav class=\"footer-links\" aria-label=\"RPS footer\"><a href=\"/rps/\">RPS Agent Lab</a></nav>"
        "</div></footer></body></html>"
    )
    html = _inject_html(lab_html, "rps")
    assert html.count("<footer") == 1
    assert '<footer class="aix-injected-footer">' not in html
    assert "2026 AIX Protodyne" in html
    assert "2026 RPS Agent Lab" not in html
    assert 'href="/rps/">RPS Agent Lab</a>' in html
    assert 'href="/contact">Contact Us</a>' in html
    assert 'href="/privacy">Privacy</a>' in html
    assert 'href="/toc">AIX TOC</a>' in html
    assert 'id="aix-subpage-back"' in html


def test_lab_without_footer_gets_injected_footer():
    from aix_web.lab_theme_wrapper import _inject_html

    html = _inject_html("<html><body><main>Lab</main></body></html>", "polyfolds")
    assert '<footer class="aix-injected-footer">' in html
    assert "2026 AIX Protodyne" in html
    assert 'href="/contact">Contact Us</a>' in html
