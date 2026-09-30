"""Decision memo rendering (SPEC FR-4): Markdown via Jinja2, HTML via markdown-it-py."""

from __future__ import annotations

from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined
from markdown_it import MarkdownIt

_ENV = Environment(
    loader=PackageLoader("pv", "templates"),
    undefined=StrictUndefined,
    trim_blocks=False,
    lstrip_blocks=False,
    keep_trailing_newline=True,
    autoescape=False,  # Markdown output; HTML is produced by markdown-it with html disabled
)

CSS = """
:root{--fg:#1d2330;--muted:#5b6475;--bg:#fff;--line:#d9dde5;--accent:#0b5cad;--warn:#8a5300}
@media (prefers-color-scheme: dark){:root{--fg:#e6e9ef;--muted:#a3abba;--bg:#12151b;--line:#2c323d;
--accent:#6aa8ff;--warn:#f0b35a}}
body{font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif;color:var(--fg);background:var(--bg);
max-width:980px;margin:0 auto;padding:24px 16px}
h1{font-size:1.6rem}
h2{font-size:1.2rem;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:2rem}
table{border-collapse:collapse;width:100%;display:block;overflow-x:auto;font-size:.9rem}
th,td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
td:nth-child(n+2){font-variant-numeric:tabular-nums}code{font-size:.85em}a{color:var(--accent)}
blockquote{border-left:4px solid var(--warn);margin:0;padding:4px 12px;color:var(--warn)}
em{color:var(--muted)}
"""


def render_markdown(results: dict[str, Any]) -> str:
    return _ENV.get_template("memo.md.j2").render(r=results)


def render_html(markdown: str, title: str) -> str:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    body = md.render(markdown)
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{_esc(title)}</title><style>{CSS}</style></head><body>\n{body}</body></html>\n"
    )


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
