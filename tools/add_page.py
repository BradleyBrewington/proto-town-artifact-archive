#!/usr/bin/env python
"""Insert or update one page entry in pages.json (idempotent by filename).

Usage:
  add_page.py --file F.html --title "T" --section "S" --desc "D" --date YYYY-MM-DD

If a page with the same --file already exists it is updated in place (and moved
to the requested section if that changed); otherwise it is appended. New sections
are created at the end. Called by publish.sh; usable by hand.
"""
import argparse
import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "pages.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--section", required=True)
    ap.add_argument("--desc", default="")
    ap.add_argument("--date", required=True)
    a = ap.parse_args()

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = {"file": a.file, "title": a.title, "date": a.date, "desc": a.desc}

    # Remove any existing entry with this filename (so re-publish updates in place).
    for sec in m["sections"]:
        sec["pages"] = [p for p in sec["pages"] if p["file"] != a.file]

    target = next((s for s in m["sections"] if s["name"] == a.section), None)
    if target is None:
        target = {"name": a.section, "pages": []}
        m["sections"].append(target)
    target["pages"].append(entry)

    # Drop any section left empty by a move.
    m["sections"] = [s for s in m["sections"] if s["pages"]]

    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"pages.json updated: {a.file} -> section '{a.section}'")


if __name__ == "__main__":
    main()
