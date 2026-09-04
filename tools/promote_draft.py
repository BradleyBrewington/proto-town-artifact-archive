#!/usr/bin/env python
"""Promote edits from a frontend-draft studio session into the archive.

The draft-studio loop (~/.claude/skills/frontend-draft) serves a disposable
copy of this repo; the user and Claude edit pages there. This script is the
promote step: it takes every root-level *.html that differs from the repo copy
(index.html excluded — it is generated from pages.json), secret-gates it,
copies it in, syncs the page's <title> and bumps its date in pages.json,
regenerates index.html, and commits. Push is explicit, matching the
frontend-draft rule that going live is a decision, not a side effect.

New pages found in the draft (no repo counterpart) need catalog metadata, so
they are promoted only when --section is given (title from <title>, desc from
--desc); otherwise they are listed and skipped — publish them individually
with tools/publish.sh.

Usage:
  promote_draft.py [DRAFT_DIR] [--push] [--section "S" [--desc "D"]] [--dry-run]

DRAFT_DIR defaults to ~/.draft-studio/<repo-name>/draft.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # page titles contain non-cp1252 chars

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "pages.json"

SECRET_RE = re.compile(
    r"sk-ant-[A-Za-z0-9_-]{20,}"
    r"|[0-9]{9,10}:AA[A-Za-z0-9_-]{30,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----")


def page_title(html: str) -> str | None:
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    return m.group(1).strip() if m else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", nargs="?", default=None)
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--section", default=None, help="section for NEW pages")
    ap.add_argument("--desc", default="", help="desc for NEW pages")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    draft = Path(a.draft) if a.draft else \
        Path.home() / ".draft-studio" / ROOT.name / "draft"
    if not draft.is_dir():
        sys.exit(f"error: no draft at {draft} — start a frontend-draft session first")

    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    known = {p["file"]: p for sec in m["sections"] for p in sec["pages"]}
    today = datetime.date.today().isoformat()

    changed, new, skipped = [], [], []
    for src in sorted(draft.glob("*.html")):
        if src.name == "index.html":
            continue
        text = src.read_text(encoding="utf-8")
        if SECRET_RE.search(text):
            sys.exit(f"ABORT: possible real secret in draft {src.name} — remove it first")
        dst = ROOT / src.name
        if dst.exists() and dst.read_text(encoding="utf-8") == text:
            continue
        if src.name in known or dst.exists():
            changed.append((src, text))
        elif a.section:
            new.append((src, text))
        else:
            skipped.append(src.name)

    if not changed and not new:
        print("nothing to promote — draft matches the repo" +
              (f" (skipped new pages needing --section: {', '.join(skipped)})" if skipped else ""))
        return

    for src, text in changed + new:
        print(f"{'would promote' if a.dry_run else 'promoting'}: {src.name}")
        if a.dry_run:
            continue
        (ROOT / src.name).write_text(text, encoding="utf-8")
        title = page_title(text)
        entry = known.get(src.name)
        if entry:
            if title and title != entry["title"]:
                print(f"  title: '{entry['title']}' -> '{title}'")
                entry["title"] = title
            entry["date"] = today
        else:
            sec = next((s for s in m["sections"] if s["name"] == a.section), None)
            if sec is None:
                sec = {"name": a.section, "pages": []}
                m["sections"].append(sec)
            sec["pages"].append({"file": src.name, "title": title or src.stem,
                                 "date": today, "desc": a.desc})
    if skipped:
        print(f"skipped new pages (need --section): {', '.join(skipped)}")
    if a.dry_run:
        return

    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools" / "gen_index.py")], check=True)

    names = [s.name for s, _ in changed + new]
    subprocess.run(["git", "-C", str(ROOT), "add", "pages.json", "index.html", *names],
                   check=True)
    subprocess.run(["git", "-C", str(ROOT), "commit", "-q", "-m",
                    f"Promote from draft studio: {', '.join(names)}"], check=True)
    if a.push:
        subprocess.run(["git", "-C", str(ROOT), "push", "-q", "origin", "main"],
                       check=True)
        base = m.get("base_url")
        print("pushed — Pages rebuilds in ~30-60s" if base else "pushed (private repo)")
        for n in names:
            print(f"  {base}/{n}" if base else f"  {ROOT / n}")
    else:
        print("committed locally. To go live: git -C", ROOT, "push origin main")


if __name__ == "__main__":
    main()
