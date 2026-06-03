# Rolling actualized examples up to the parent (upstream) repo

This fork (`IgorShevchik/b24-rest-docs`) is where the b24jssdk example actualization is
developed and validated. Finished sections are then contributed **upstream** to the parent
documentation repo. This runbook is the process for that hand-off.

> The actualization agent's GitHub access is restricted to this fork, so it cannot open a PR
> on the parent. The agent **prepares** a clean content patch here; a maintainer applies it to
> the parent and opens the upstream PR.

## Scope — what goes upstream vs what stays in the fork

**Goes upstream (content only):**
- `api-reference/**` — the actualized `- JS (TS)` / `- JS (UMD)` examples (and nothing else on those pages;
  prose, parameter tables, response sections are unchanged by actualization).

**Stays in the fork (never sent upstream):**
- `.actualize/**` — the process tooling (validate.py, record.py, run-batch.sh, PROMPT*, ledger…).
- `.github/workflows/validate-examples.yml`, `.gitattributes` — our CI/merge infrastructure.

Patches under `.actualize/upstream/*.patch` are content-only by construction (scoped to
`api-reference/**`), so applying one to the parent cannot leak fork tooling.

## Ready to ship

| Section | Patch | State |
|---|---|---|
| `user/` | `.actualize/upstream/user-section.patch` | 10 method pages, all `validate.py` PASS, ledger 0 drift |

The `user/` patch was generated from this fork's `user/` actualization and verified to apply
cleanly onto the pre-actualization (legacy = parent-equivalent) tree.

## Apply a section to the parent

```bash
# 1. fresh, up-to-date clone of the PARENT repo (not this fork)
git clone <parent-repo-url> b24-docs-upstream
cd b24-docs-upstream
git checkout -b actualize/user-examples        # one branch per section

# 2. apply the content patch (--3way resolves automatically if the parent drifted a little)
git apply --3way /path/to/user-section.patch
#   if it reports conflicts: the parent moved under those files — re-actualize the drifted
#   file(s) in the fork, regenerate the patch, and retry (see "Drift" below)

# 3. (optional) validate locally if you have the toolchain; the fork already validated these
# 4. commit + push + open the upstream PR
git add api-reference/user
git commit -m "docs(user): actualize JS examples to TS + UMD (b24jssdk actions API)"
git push origin actualize/user-examples
```

## Upstream PR conventions

- **One section = one PR** — matches our internal policy and keeps upstream review small.
- **Title:** `docs(<section>): actualize JS examples to TS + UMD (b24jssdk actions API)`.
- **Body, mention:** examples target `@bitrix24/b24jssdk@1` (the actions API); the old
  `callMethod` / `callListMethod` / `fetchListMethod` are removed in SDK 2.0. Non-JS tabs
  (`cURL`, `PHP`, `BX24.js`, `PHP CRest`) are intentionally unchanged. `user-get.md` carries
  four independent examples.
- Follow the parent's own contribution rules (CLA, commit style) if they differ.

## Drift (parent moved since we forked)

The patch is a snapshot. If `git apply --3way` reports conflicts on a file, the parent changed
that page after our fork point. Resolve by re-actualizing the **current** upstream version of
that file in the fork (run the agent + `validate.py`), regenerate the section patch, and retry.
Validate in the fork **before** sending — never ship an example that has not passed `validate.py`.

## Regenerating a section patch (in this fork)

```bash
# diff of a merged section PR, scoped to its content (excludes ledger/.actualize):
git diff <section-pr-squash>^ <section-pr-squash> -- api-reference/<section>/ \
  > .actualize/upstream/<section>-section.patch
```

## Next sections

`crm` (~404 pages, includes multi-example pages now handled by the validator), then `disk`,
`calendar`, … — same flow: actualize + validate in the fork → generate a content patch → a
maintainer opens the upstream PR.
