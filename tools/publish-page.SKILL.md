---
name: publish-page
description: Publish, list, or update self-contained HTML pages on GitHub Pages — the account-agnostic replacement for claude.ai artifacts. Use for "publish a page", "make this a page", "list my pages", "update my page", "promote the draft", and INSTEAD of the Artifact tool for any project content. Works from any project on this machine.
---

# Publish-page: GitHub Pages instead of artifacts

Project content is never published as a claude.ai artifact (artifact ownership
is per-account; the user has two accounts). Instead, pages live in git repos the
user owns, hosted on GitHub Pages, with a data catalog (`pages.json`) that any
agent on any account can read. The tooling lives IN the repos, so cloning a repo
brings the whole pipeline with it.

## Repos

| Repo | Path | Visibility | URL |
|---|---|---|---|
| proto-town-artifact-archive | `C:\dev\artifact-archive` | PUBLIC on Pages | https://bradleybrewington.github.io/proto-town-artifact-archive/ |
| bd-artifact-archive | `C:\dev\bd-artifact-archive` | PRIVATE, no Pages | open files locally |

Default to the public repo. BD / competitive / sensitive content goes to the
private repo — ask if unsure. Each repo's `pages.json` is the catalog and holds
`base_url` (absent in the private repo; the tools adapt automatically).

**Bootstrap** — if a repo path is missing (fresh machine/agent):
`gh repo clone BradleyBrewington/proto-town-artifact-archive C:/dev/artifact-archive`
(same pattern for `bd-artifact-archive`). Everything below works after a clone.

Python is invoked as `py` on this machine (`python`/`python3` are Store-alias
stubs); the scripts force UTF-8 stdout themselves.

## Publish a new page

1. Invoke the `artifact-design` skill first to calibrate the design treatment
   (a doc, a report, and a landing page each warrant different craft).
2. Author a **self-contained** HTML file (scratchpad is fine): inline all
   CSS/JS, embed images/fonts as data: URIs, no external URLs. Theme-aware
   (light/dark) and responsive. Full document, `<!doctype html>` … `</html>`.
   If the user supplied an .html path, use it directly.
3. From the repo directory:
   `bash tools/publish.sh <file> --title "Human Title" --section "Section Name" --desc "one line"`
   Reuse an existing section name from `pages.json` when one fits. The script
   secret-gates the file, updates the catalog, regenerates the index, commits,
   and pushes.
4. Report the live URL it prints. Pages rebuilds in ~30-60 s;
   `curl -s -o /dev/null -w "%{http_code}" <url>` → 200 confirms.

## List pages (the /artifacts replacement)

`py tools/list_pages.py` in either repo (`--json` for structured output).
When the user asks "what pages do I have", run it in both repos.

## Update a page

Re-run `publish.sh` with the same `--slug` — replaces the page in place at the
same URL and refreshes its catalog entry.

## Promote a frontend-draft session

When the user edited pages via the `frontend-draft` skill on an archive repo
(`studio.py C:/dev/artifact-archive`), promote with:
`py tools/promote_draft.py [--dry-run] [--push]`
It takes every changed root-level page from `~/.draft-studio/<repo>/draft`
(index.html excluded — it is generated), secret-gates them, syncs each page's
`<title>` and date into `pages.json`, regenerates the index, and commits once.
Ask before `--push` — going live is the user's decision. New pages drafted from
scratch need `--section "S" [--desc "D"]`, or publish them via publish.sh.

## Rules

- Never hand-edit `index.html` in these repos — always regenerated from `pages.json`.
- Never publish real secrets; the tools grep-gate, but don't rely on it.
- Never `git reset --hard` in an archive repo with uncommitted tool changes.
- Mirroring a claude.ai artifact into the archive: WebFetch its URL from a
  session logged into the OWNING account, then `tools/strip_artifact.py in out`,
  then publish.sh.
