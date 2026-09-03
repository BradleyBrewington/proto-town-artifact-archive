# Proto-Town Artifact Archive

Static mirror of claude.ai Code artifacts from the Proto-Town / AI-in-Physical-Space
project, consolidated from **two claude.ai accounts** into one place so the pages are
readable regardless of which account is logged in.

Open `index.html` for the catalog.

## How pages get here

Artifacts on claude.ai are self-contained HTML (strict CSP, everything inlined), so
they work as plain static files. The server wraps each one in a skeleton that injects
a ~14 KB "frame-runtime" script (theme sync + live-edit plumbing for the claude.ai
shell) which is inert outside that shell. The mirror step:

1. In a Claude Code session logged into the owning account, ask Claude to fetch the
   artifact (`WebFetch` on the `claude.ai/code/artifact/{uuid}` URL returns the raw
   HTML for artifacts the logged-in account owns — plain `curl` does NOT work, it
   gets a Cloudflare 403).
2. Run `tools/strip_artifact.py IN.html OUT.html` — removes the frame-runtime block
   and hoists the body-level `<title>` into `<head>`. Nothing else is touched.
3. Add a row to `index.html`, commit, push.

Google Fonts `<link>` tags in some pages were CSP-blocked on claude.ai (silent
system-font fallback) but load normally when self-hosted — the pages here can
actually look *better* than the originals.

## Contents

| Page | Source artifact (account) | Archived |
|---|---|---|
| overlap-ensemble-act.html | 37a6995e (A) | 2026-09-03 |
| so101-data-factory.html | cc80c2fc (B) | 2026-09-03 |
| so101-factory-wiring.html | ba0ed158 (A) | 2026-09-03 |
| so101-speed-loop.html | 9baaaba8 (A) | 2026-09-03 |
| speed-loop-session-one.html | 8f352c97 (A) | 2026-09-03 |
| evidence-chains.html | cc94e646 (A) | 2026-09-03 |
| behavior-ledger.html | 0bc5d025 (A) | 2026-09-03 |
| project-history.html | a81d59c6 (A) | 2026-09-03 |
| sbir-coverage-audit.html | 8587c5e3 (A) | 2026-09-03 |

Account A = the account owning the "Overlap-Ensemble ACT" note; account B = the one
owning "SO101 Data Factory".

**Still missing (account B):** Start-Point Range (37ede268), SO101 Factory Wiring
earlier variant (1938b946), Claude touches three rolls of tape (3de0452c). Log into
account B and repeat the mirror step.

## Hosting

This repo is intended for GitHub Pages (serve from root of `main`). Note: on a free
GitHub plan, Pages requires the repo to be **public** — everything in here becomes
world-readable, including the SBIR audit (business-development intelligence). Keep
the repo private until that trade-off is deliberate, or split sensitive pages into a
separate private repo.

The claude.ai originals remain live and editable; this archive is a mirror, not a
replacement. When an artifact is updated on claude.ai, re-run the mirror step to
refresh its page here.
