#!/usr/bin/env bash
# Publish one self-contained HTML page to the archive and push it live.
#
# Usage:
#   tools/publish.sh SRC.html --title "T" --section "S" [--desc "D"] \
#       [--slug name.html] [--date YYYY-MM-DD] [--no-push]
#
# Steps: secret-gate the file -> copy it in under its slug -> update pages.json
# -> regenerate index.html -> commit -> push. Prints the live GitHub Pages URL.
# This is the replacement for creating a claude.ai artifact.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${PYTHON:-py}"  # Windows launcher; override with PYTHON=... on other OSes
BASE_URL="https://bradleybrewington.github.io/proto-town-artifact-archive"

SRC="" TITLE="" SECTION="" DESC="" SLUG="" DATE="" PUSH=1
while [ $# -gt 0 ]; do
  case "$1" in
    --title)   TITLE="$2"; shift 2 ;;
    --section) SECTION="$2"; shift 2 ;;
    --desc)    DESC="$2"; shift 2 ;;
    --slug)    SLUG="$2"; shift 2 ;;
    --date)    DATE="$2"; shift 2 ;;
    --no-push) PUSH=0; shift ;;
    -*) echo "unknown flag: $1" >&2; exit 2 ;;
    *)  SRC="$1"; shift ;;
  esac
done

[ -n "$SRC" ]     || { echo "error: SRC html file required" >&2; exit 2; }
[ -f "$SRC" ]     || { echo "error: no such file: $SRC" >&2; exit 2; }
[ -n "$TITLE" ]   || { echo "error: --title required" >&2; exit 2; }
[ -n "$SECTION" ] || { echo "error: --section required" >&2; exit 2; }
[ -n "$SLUG" ]    || SLUG="$(basename "$SRC")"
case "$SLUG" in *.html) ;; *) SLUG="$SLUG.html" ;; esac
[ -n "$DATE" ]    || DATE="$(date +%F)"

# --- secret gate: refuse to publish real credentials ---------------------------
if grep -Eq 'sk-ant-[A-Za-z0-9_-]{20,}|[0-9]{9,10}:AA[A-Za-z0-9_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----' "$SRC"; then
  echo "ABORT: possible real secret (Anthropic key / Telegram token / private key) in $SRC" >&2
  echo "       Remove it or use a placeholder, then re-run." >&2
  exit 1
fi

cp "$SRC" "$REPO/$SLUG"
"$PYTHON" "$REPO/tools/add_page.py" --file "$SLUG" --title "$TITLE" \
  --section "$SECTION" --desc "$DESC" --date "$DATE"
"$PYTHON" "$REPO/tools/gen_index.py"

cd "$REPO"
git add "$SLUG" pages.json index.html
git commit -q -m "Publish: $TITLE" || { echo "nothing to commit"; }
if [ "$PUSH" -eq 1 ]; then
  git push -q origin main
  echo "published (pushed). Pages rebuilds in ~30-60s:"
else
  echo "committed locally (--no-push). To go live: git push origin main"
fi
echo "  $BASE_URL/$SLUG"
