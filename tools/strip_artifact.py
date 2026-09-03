#!/usr/bin/env python
"""Convert a claude.ai artifact HTML capture into a self-contained static page.

Artifacts served from claude.ai/code/artifact/{uuid} are the author's HTML
body wrapped in a server skeleton that injects one large "frame-runtime"
script (theme sync, live-patch plumbing, telemetry postMessage to the
claude.ai shell). Outside that shell the script is inert but dead weight,
so strip it. Everything else (charset, viewport, CSS reset, author content)
is kept verbatim.

Also hoists a body-level <title> into <head> (the server leaves it in the
body; browsers tolerate it, but it's invalid HTML).

Usage: strip_artifact.py IN.html OUT.html
"""
import re
import sys
from pathlib import Path


def strip(html: str) -> str:
    html = re.sub(
        r"<!-- frame-runtime -->.*?<!-- /frame-runtime -->",
        "", html, count=1, flags=re.S)
    m = re.search(r"<title>.*?</title>", html, flags=re.S)
    if m and re.search(r"<body[^>]*>", html[: m.start()]):
        title = m.group(0)
        html = html[: m.start()] + html[m.end():]
        html = re.sub(r"</head>", title + "</head>", html, count=1)
    return html


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    out = strip(src.read_text(encoding="utf-8"))
    dst.write_text(out, encoding="utf-8")
    print(f"{src.name}: {src.stat().st_size:,} -> {len(out.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    main()
