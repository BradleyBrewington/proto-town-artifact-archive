#!/usr/bin/env python
"""List the published pages — the account-agnostic replacement for /artifacts.

Reads pages.json (the catalog is data) and prints every page with its live URL,
newest first within each section. Works identically in any archive repo that
follows the pages.json convention; the private BD repo simply has no base_url,
so its pages print as local files.

Usage:
  list_pages.py            human-readable listing
  list_pages.py --json     machine-readable (for other tools / Claude)
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # page titles/descs contain non-cp1252 chars

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "pages.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base = m.get("base_url")  # absent/None in private repos with no Pages

    if a.json:
        out = []
        for sec in m["sections"]:
            for p in sec["pages"]:
                out.append({**p, "section": sec["name"],
                            "url": f"{base}/{p['file']}" if base else str(ROOT / p["file"])})
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    n = sum(len(s["pages"]) for s in m["sections"])
    where = base if base else f"{ROOT}  (PRIVATE — no Pages, open locally)"
    print(f"{m['heading']} — {n} pages — {where}\n")
    for sec in m["sections"]:
        print(f"[{sec['name']}]")
        for p in sorted(sec["pages"], key=lambda p: p["date"], reverse=True):
            loc = f"{base}/{p['file']}" if base else p["file"]
            print(f"  {p['date']}  {p['title']}")
            print(f"              {loc}")
            if p.get("desc"):
                print(f"              {p['desc']}")
        print()


if __name__ == "__main__":
    main()
