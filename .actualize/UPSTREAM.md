# Rolling actualized examples up to the parent (upstream) repo

This fork (`IgorShevchik/b24-rest-docs`) is where the b24jssdk example actualization is
developed and validated. Finished sections are then contributed **upstream** to the parent
docs repo `bitrix-tools/b24-rest-docs`. This runbook is that hand-off — and it is now encoded
in `.actualize/upstream/contribute-to-upstream.sh`, so "do it the way that worked" means
**run that script**.

> The actualization agent's GitHub access is restricted to this fork, so it cannot open a PR
> on the parent. The script does everything up to that point — builds, verifies and pushes one
> branch per section to the fork, and prints a compare URL per section. A human clicks
> **"Create pull request"** on each (base = `bitrix-tools/b24-rest-docs : main`).

## The flow (what the script does)

```bash
# from a CLEAN fork clone:
.actualize/upstream/contribute-to-upstream.sh            # DRY: auto-detect + verify, push nothing
PUSH=1 .actualize/upstream/contribute-to-upstream.sh     # push the verified branches + print URLs
```

1. **SYNC** — fetch fresh `origin/main` (fork) and `upstream/main` (parent). Every section is
   branched off **fresh `upstream/main`**, never off fork `main`: the parent keeps moving (it
   adds pages after our fork point), so branching off it keeps each PR's diff to *only* our
   example changes and avoids "reverting" newer upstream edits.
2. **SELECT** — a section ships **iff** `upstream/main` still has legacy jsSDK calls in it
   **and** the fork has fully actualized it (0 legacy left, ≥1 `- JS (TS)` page). That rule
   auto-skips sections the parent already modernised (no duplicates) and any half-finished
   section. Pass section labels/paths as args to ship a specific set; with no args the set is
   auto-detected. Granularity mirrors our PR policy: each `api-reference/crm/<sub>` is its own
   section; every other `api-reference/<dir>` is one section.
3. **BUILD** — one branch `actualize/<slug>` per section off `upstream/main`, copying in **only**
   that section's `api-reference/<section>` content from the fork. No `.actualize/` tooling, no
   `.github/` CI, no ledger — content only, by construction.
4. **VERIFY** — the gate that makes the hand-off trustworthy. Each built branch must pass **all**:
   - every page has **both** `- JS (TS)` and `- JS (UMD)` (count TS == count UMD > 0),
   - **0** legacy calls (`$b24.callMethod` / `callListMethod` / `fetchListMethod`),
   - **0** files touched outside `api-reference/<section>/`,
   - **0** tooling/CI files (`.actualize/`, `.github/`).
   If **any** selected section fails, the run aborts and **nothing is pushed** (fail-fast).
5. **SHIP** — **dry by default**: print the manifest + compare URLs and remove the temp branches
   (tree left exactly as found). `PUSH=1` pushes the verified branches to the fork (with retry)
   and prints the URLs. The script never pushes to upstream.

The offline test `.actualize/tests/test_contribute_upstream.sh` (run in CI) covers all of this:
auto-detect selection, the verify gate rejecting a TS-only page, the `PUSH=1` path, and the
"already upstream → nothing to ship" case.

> **grep gotcha** (this bit us once, hence the note): `git grep` patterns that start with `-`
> — like `- JS (TS)` — must be passed as `-F -e '<pattern>'`, and options (`--cached`, a `<rev>`)
> must come **before** the pattern. Otherwise git reads the leading `-` as an unknown switch and
> silently reports 0 matches.

## Scope — what goes upstream vs what stays in the fork

**Goes upstream (content only):** `api-reference/**` — the actualized `- JS (TS)` / `- JS (UMD)`
examples and nothing else on those pages (prose, parameter tables, response sections are
untouched by actualization; other language tabs are byte-for-byte unchanged).

**Stays in the fork (never sent upstream):** `.actualize/**` (the tooling — validate.py,
record.py, run-batch.sh, run-section.sh, contribute-to-upstream.sh, PROMPT*, ledger…) and
`.github/workflows/**`, `.gitattributes` (our CI/merge infrastructure). The script enforces this
by construction (it only copies the section path) and the verify gate re-checks it.

## Merged into upstream ✅

One PR per section, all passed `validate.py` in the fork, ledger 0 drift.

| Batch | Sections | Date |
|---|---|---|
| Tier-1 CRM + calendar | `crm/status` (8), `crm/deals` (29), `crm/leads` (23), `crm/companies` (21), `crm/currency` (12), `calendar` (20) | 2026-06-08 |
| Tier-2 (9 sections) | `crm/contacts` (17), `messageservice` (5), `telephony` (29), `disk` (37), `document-generator` (29), `booking` (38), `sonet-group` (44), `imopenlines` (50), `catalog` (149) | 2026-06-16 |
| `rest-v3` | `rest-v3` (74) | 2026-06-16 |

> Merge **confirmed by a fork↔upstream byte-identity check on 2026-06-16** — our examples are
> present verbatim in `upstream/main`, with 0 legacy in every shipped section.
>
> `rest-v3` drift handled at hand-off: upstream had added 8 legacy pages after our fork point
> (`humanresources/employee/*`, `humanresources/node-communication/*`) and updated the
> `humanresources` TOC/index; these were re-synced from `upstream/main` and actualized, TOC/index
> adopted from upstream — so the PR reverted no newer upstream content.
>
> `user/` and `tasks/` were **dropped from the hand-off**: upstream actualized those pages itself
> (found during a fork↔upstream sync), so the auto-detect rule skips them (no legacy upstream →
> not selected).

## In review (pushed, PRs to open/awaiting) ⏳

_Nothing pending._ As of **2026-06-16** every shipped section is merged into `upstream/main`
(verified by byte-identity). `contribute-to-upstream.sh` with no args auto-detects **nothing to
ship** — each section fully actualized in the fork is already upstream. New hand-offs unlock only
after the **Remaining in the fork** sections (below) are finished.

## Remaining in the fork (state as of 2026-06-16 — resume Mon)

Fork actualization: **1553 pages done, 80 with legacy `$b24.callMethod` left.** But **75 of those 80
are in deprecated `outdated/` folders** — likely **skip** (no point modernizing deprecated docs;
upstream may not want SDK examples there):

| Bucket | Pages | Action |
|---|---|---|
| `crm/outdated/*` | 71 | deprecated → decide skip |
| `outdated/*` (top-level) | 4 | deprecated → decide skip |
| `chat-bots/*` | 2 | **live → actualize** |
| `files/*` | 1 | **live → actualize** |
| `departments/*` | 1 | **live → actualize** |
| `bizproc/*` | 1 | **live → actualize** |

**Next session (Mon):** (1) confirm we skip the deprecated `outdated/` pages; (2) actualize the **5
live pages** (chat-bots, files, departments, bizproc) via `run-section.sh`; (3) once their sections
are 0-legacy in the fork, `contribute-to-upstream.sh` (no args) will auto-detect + ship them. After
that the corpus is effectively complete (modulo the deprecated skip).

## Upstream PR conventions

- **One section = one PR** — keeps upstream review small.
- **Title:** `docs(<section>): actualize JS examples to TS + UMD`.
- **Body:** `.actualize/upstream/PR-TEMPLATE.md` (mention: examples target the actions API;
  `callMethod` / `callListMethod` / `fetchListMethod` are removed in SDK 2.0; non-JS tabs and
  page prose are intentionally unchanged; list methods use `call.make` with `start`).
- Follow the parent's own contribution rules (CLA, commit style) if they differ.

## Reviewer asked for a change?

Fix it in the **fork's `main`** (re-actualize + `validate.py`), then re-run
`PUSH=1 contribute-to-upstream.sh <section>`. The branch is rebuilt off fresh `upstream/main`
and force-updated; the open PR refreshes automatically. Never ship an example that has not passed
`validate.py` in the fork.

## Drift (parent moved under a page we're shipping)

Because each branch is rebuilt off **fresh** `upstream/main` every run, routine upstream movement
is absorbed automatically. If the parent edited the *same page* we actualized, the eventual PR
merge may conflict: re-actualize the **current** upstream version of that page in the fork, re-run
`validate.py`, and re-run the script for that section.
