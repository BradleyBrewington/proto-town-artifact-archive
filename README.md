# Proto-Town Pages

Self-contained HTML pages — design notes, session reports, audits — authored as
files **you own** and served via **GitHub Pages**. This is the replacement for
claude.ai artifacts: same self-contained-HTML page, but the output is a file in
a repo you control (editable, deletable, access-controlled, shareable by plain
URL, no per-account ownership trap).

Live catalog: **https://bradleybrewington.github.io/proto-town-artifact-archive/**
Open `index.html` locally for the same catalog.

BD / competitive material does **not** go here — it goes in the separate
**private** `bd-artifact-archive` repo. Check before publishing.

## Publish a new page (the main workflow)

Author a self-contained HTML file (inline everything — same CSP-safe rules as an
artifact; no external CSS/JS/font/image URLs), then:

```sh
tools/publish.sh path/to/page.html \
  --title "Human Title" \
  --section "SO-101 arm · data factory" \
  --desc "One-line description for the catalog." \
  [--slug my-page.html] [--date YYYY-MM-DD] [--no-push]
```

It runs a **secret gate** (aborts on a real Anthropic key, Telegram token, or
private key), copies the file in under its slug, updates `pages.json`, regenerates
`index.html` from that manifest, commits, and pushes. It prints the live URL;
Pages rebuilds in ~30-60 s. Re-running with the same slug updates the page in place.

The catalog is **data, not hand-edited HTML**: `pages.json` is the source of truth
and `tools/gen_index.py` renders it, so the index can never drift from what was
actually published. To restyle the index, edit `gen_index.py`; to fix a title or
move a page between sections, edit `pages.json` (or re-publish) and run
`py tools/gen_index.py`.

`publish.sh` defaults to the Windows `py` launcher; on other machines run it as
`PYTHON=python3 tools/publish.sh ...`.

## Import an existing claude.ai artifact (one-time, legacy)

Artifacts are already self-contained HTML wrapped in a server skeleton that injects
a ~14 KB "frame-runtime" script (inert outside claude.ai). To mirror one:

1. In a Claude Code session **logged into the account that owns the artifact**,
   `WebFetch` the `claude.ai/code/artifact/{uuid}` URL — it returns the raw HTML
   for owned artifacts (plain `curl` gets a Cloudflare 403; a wrong login gets
   "not found"). Large captures auto-save to a tool-results file.
2. `py tools/strip_artifact.py IN.html OUT.html` — removes the frame-runtime block
   and hoists the body-level `<title>` into `<head>`. Nothing else is touched.
3. Publish the stripped file with `tools/publish.sh` as above.

Google Fonts `<link>` tags that were CSP-blocked on claude.ai load normally when
self-hosted, so mirrored pages can look *better* than the originals.

## Hosting

Public repo, served via GitHub Pages from the root of `main`; `.nojekyll` keeps
Jekyll off so files serve verbatim. `gh` is authed as BradleyBrewington.
