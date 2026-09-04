#!/usr/bin/env python
"""Regenerate index.html from pages.json.

The catalog is data (pages.json), not hand-edited HTML, so it can never drift
from what publish.sh actually added. Run automatically by publish.sh; safe to
run by hand too:  python tools/gen_index.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "pages.json"
OUT = ROOT / "index.html"

STYLE = """<style>
:root{
  --bg:#f4f4f1; --panel:#fbfbf9; --ink:#20241f; --muted:#68706a; --line:#d7d9d2;
  --acc:#3d6b52;
  --mono:ui-monospace,"Cascadia Mono",Consolas,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#181b19; --panel:#20241f; --ink:#e5e7e2; --muted:#98a09a; --line:#333831; --acc:#7fb597;}}
:root[data-theme="dark"]{
  --bg:#181b19; --panel:#20241f; --ink:#e5e7e2; --muted:#98a09a; --line:#333831; --acc:#7fb597;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Charter,Georgia,serif}
main{max-width:44rem;margin:0 auto;padding:3rem 1.25rem 5rem}
.eyebrow{font-family:var(--mono);font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);margin:0 0 .5rem}
h1{font-size:1.8rem;line-height:1.15;margin:0 0 .4rem;text-wrap:balance}
.sub{color:var(--muted);margin:0 0 2rem;font-size:.98rem}
h2{font-size:1.05rem;font-family:var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600;margin:2.4rem 0 .6rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}
ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:.55rem}
li{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:.65rem .9rem}
li a{color:var(--ink);font-weight:700;text-decoration:none}
li a:hover{color:var(--acc);text-decoration:underline}
li .d{display:block;color:var(--muted);font-size:.88rem;margin-top:.12rem}
li .m{font-family:var(--mono);font-size:.72rem;color:var(--muted);float:right}
.note{border-left:3px solid var(--acc);background:var(--panel);padding:.55rem .9rem;border-radius:0 4px 4px 0;font-size:.92rem;margin-top:2.2rem;color:var(--muted)}
:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
</style>"""


def esc(s: str) -> str:
    """Escape element text: keep apostrophes/quotes literal (they are safe here)."""
    return html.escape(s, quote=False)


def esc_attr(s: str) -> str:
    """Escape attribute values (href): quotes must be encoded."""
    return html.escape(s, quote=True)


def render(m: dict) -> str:
    parts = [
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{esc(m.get('title', m.get('heading', 'Artifact Archive')))}</title>",
        STYLE + "</head><body>",
        "<main>",
        f'<p class="eyebrow">{esc(m["eyebrow"])}</p>',
        f'<h1>{esc(m["heading"])}</h1>',
        f'<p class="sub">{esc(m["sub"])}</p>',
    ]
    for sec in m["sections"]:
        parts.append(f'\n<h2>{esc(sec["name"])}</h2>')
        parts.append("<ul>")
        for p in sec["pages"]:
            parts.append(
                f'<li><span class="m">{esc(p["date"])}</span>'
                f'<a href="{esc_attr(p["file"])}">{esc(p["title"])}</a>'
                f'<span class="d">{esc(p["desc"])}</span></li>'
            )
        parts.append("</ul>")
    note = m.get("note")
    if note:
        # note may contain intentional inline HTML (e.g. <em>), so it is not escaped.
        parts.append(f'\n<p class="note">{note}</p>')
    parts.append("</main>\n</body></html>\n")
    return "\n".join(parts)


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.write_text(render(m), encoding="utf-8")
    n = sum(len(s["pages"]) for s in m["sections"])
    print(f"index.html regenerated: {n} pages across {len(m['sections'])} sections")


if __name__ == "__main__":
    main()
