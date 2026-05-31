# Follow-ups (deferred review items)

GitHub Issues are disabled in the repository, so review items that do not block the tooling merge
are recorded here. When Issues are enabled — migrate these.

## 1. [major] SDK version policy: typecheck `@1.2.0` vs runtime `@1` drift

Examples are typechecked against a lockfile-pinned `@bitrix24/b24jssdk`
(`typecheck/package-lock.json`), while the UMD tabs and users use the floating major tag `@1`. A
green `tsc` on the pinned version does not guarantee validity on future `1.x` releases that `@1`
will pull in → the documentation may silently diverge from the SDK, and CI will not notice.

Proposal:
- a periodic CI job (`schedule` + `workflow_dispatch`): `validate.py` over all `done` files in the
  ledger against `@1 latest` (not against the pin). Per the multi-review outcome — make it
  **failing** (not informational): a green `tsc` on the pin ≠ validity on future `1.x`; a failure =
  a signal for a mandatory lockfile bump + ledger revalidation;
- bump/rollback plan: on an SDK breaking change — update `typecheck/package.json` +
  `package-lock.json`, run `validate.py` over the ledger, and on failure — targeted
  re-actualization;
- Dependabot (npm, direct-only) already opens an SDK-bump PR as a revalidation signal;
- (optional) discuss pinning UMD to the minor `@1.2` for consistency.

## 2. [v1 implemented] Batch-runner for bulk actualization

**`.actualize/run-batch.sh`** — an orchestrator over the existing scripts (the
`validate.py`/`record.py` contracts were not changed). ⚠️ EXPERIMENTAL: not yet exercised by a real
`RUN=1` run. What it does:
- edits files with the agent (`claude -p` per `PROMPT.md`) **in parallel** (`xargs -0 -P`); the list
  comes from `remaining.py` (ledger-aware → resumable, a retry is just the next run);
- **blast-radius check** — compares the actually-changed files against the batch plan; anything
  outside the plan → revert the whole batch (`SECURITY ABORT`), no commit;
- **validates and writes the ledger serially** — one `.tscheck` sandbox, one writer (no race);
- checkpoint: commits the passing `.md` files + ledger in batches; failing ones are reverted and
  stay in `remaining`;
- safety: dry-run by default (needs `RUN=1`), refuses to start on a dirty tree, the **blast-radius
  check** (edits outside the batch plan → the whole batch is reverted, `SECURITY ABORT`) +
  prompt-hardening, a bash≥4 gate, an edit timeout (`EDIT_TIMEOUT`), the toggles
  `KEEP_FAILED` / `NO_COMMIT` / `CLAUDE_MODEL` / `CLAUDE_BIN`.

Test coverage: `tests/test_run_batch.sh` (stub agent, no network) — the dry-run gate, numeric/clean-tree
guards, PASS/FAIL+revert/SKIP, commit scope, the **blast-radius abort**, and test-documentation of the
known blast-radius limitation (writes outside the working tree).

**Done in this iteration (was deferred):**
- ✅ **prompt-injection** — an enforcement guard was added (the blast-radius check) that does not
  depend on the model's obedience: a post-check compares the changed files (tracked + untracked)
  against the batch plan, and any escape from the plan → revert the whole batch, nothing is
  committed.

Still deferred:
- **parallel validation.** We tried a per-worker `--project` sandbox via a `cp -al` clone of the
  warmed `.tscheck` — **reverted**. A hardlink clone shares inodes, but `validate.py` writes mutable
  files (`example.ts`/`umd_inner.js`) via Python `open("w")` → the write goes to the shared inode,
  parallel workers overwrite each other's code and produce cross-false verdicts (reproduced). Proper
  isolation needs either breaking the hardlinks for mutable files after the clone, or a real separate
  `node_modules` per worker (expensive). At the current scale the bottleneck is the agent edit, not
  `tsc`, so serial validation is not on the critical path;
- **`record.py` batch mode** (N paths from stdin) — for now the write runs in a serial loop (single
  writer); needed only if the write becomes the bottleneck (today the agent edit dominates);
- **blast-radius blind spots (known limitation).** The check works via `git status` and sees only
  what git reports in the working tree. NOT caught: (a) writes **outside the repository** (an absolute
  path — `~/.ssh`, `/tmp`); (b) **gitignored paths in the tree** (`.claude/`, `CLAUDE.md`); (c)
  **`.git/`** (e.g. `.git/config` → `credential.helper`). The agent's `Edit` tool is not path-limited
  (and `git clean -fd` on revert also leaves gitignored files — without `-x`). Closing this fully —
  process-level FS sandboxing of the agent (bubblewrap/firejail), or a CLI allowlist
  (`--add-dir`/`--allowedDirectories`) once it exists. Recorded in the test harness as
  test-documentation: out-of-tree (test 7) and a gitignored path in the tree (test 8); the
  `.git/config` vector has no test yet.

**Conditions before the first real `RUN=1`** (do not block the tooling merge, but are mandatory
before a corpus run):
- run on a throwaway branch with a small batch (`N=3 PAR=1`) under supervision (already in the
  script header; on `main`/`master` the script warns);
- **not on a machine with production secrets** in `~` (`~/.ssh`, etc.) — while there is no FS
  sandboxing of the agent (see the blind spots above);
- watch §1 (SDK version drift) and §5 (the CI filter `grep '- TS'`) — both cause a silent regression
  on a bulk run;
- make sure the `claude` binary supports `--permission-mode acceptEdits --allowed-tools` (the script
  only checks the binary is present, not the flags).

**Small nits (after the multi-review, low priority):**
- the batch commit message does not include a file list (visible only via `git show`); if wanted —
  the first N names in the commit body;
- `git clean -fdq -e .tscheck` on `SECURITY ABORT` does not touch gitignored escapees (without `-x`);
  acceptable for now (no harm, `.tscheck` is a cache); to tighten — `git clean -fdxq --exclude=.tscheck`.

## 3. [minor] Full bash test harness for run-batch.sh

The key branches are covered (see §2), including the negative paths: `record.py` failure (revert),
`KEEP_FAILED=1` (the file stays dirty), `git commit` failure, zero progress (`exit 3`), the
gitignored blind spot. Deferred: migration to `bats` and the case of an **interruption during the
validation phase** (a ledger row written but not committed; SIGINT in the shell harness is flaky) —
harder to reproduce in a shell harness.

## 4. [major] Batching strategy: "1 PR = 1 section"

~1542 files cannot be validated in one PR (a ~20-min CI job; an unreadable diff; no regression
isolation). Decompose by `api-reference/<section>/` (tasks — pilot ready, then crm, disk,
calendar…), each section a separate PR on top of the batch-runner (see §2). Record this as a
mandatory policy.

## 5. [major] The CI filter `grep '- TS'` silently skips files

`validate-examples.yml` runs `validate.py` only on changed `*.md` files that contain a `- TS` line.
If a file mistakenly loses `- TS` (a typo `- Ts`, an accidental tab deletion), CI passes it without
error. Options: additionally validate the PR-affected files from the ledger; or warn when a changed
`api-reference/**` file has none of the expected tabs.

## Minor (minor/nit, as needed)

- **[minor] Manual typing of result types is not verified against the live API.** The
  `type <Name>Result` types are written by hand from the JSON response on the page; `tsc` only checks
  the type's syntax, not that it matches the real response. A conscious trade-off (otherwise a live
  API stub is needed). Accepted as is.
- **[minor] `node --check` on the UMD is syntax-only.** It parses the inline script but does not
  execute it, so a wrong global or method name (`B24Js.TextX…`, `user.userfield.deletes`) passes.
  A green `node --check` proves the UMD parses, not that it runs — do not read PASS as "it works".
- **[minor] Request `params` are not type-checked.** `call.make`'s params type uses an index
  signature (`[key: string]: any`), so `tsc` validates only the result generic, not the param
  shape — a misspelled or wrong-cased param key (`SORT` vs `sort`) compiles cleanly. Option: a
  per-method JSON-schema lint (e.g. `ajv`) over `params`, hand-maintained or generated, no live API.
- **[nit][done] `getTotal()` removed.** Marked `@deprecated` / `@removed 2.0.0`; in the tasks pilot
  and in `PROMPT.md` / `PROMPT-REVIEW.md` / `README.md` replaced with `.length` + list helpers.
  Apply this in the remaining sections.
- **[minor] Tooling test coverage.** Added negative `extract` cases, `validate.main` tests
  (path-guards), `detect_method` (happy path), and a prompt-sync smoke test. Not yet covered:
  `remaining.main` (`os.walk`/`--limit`), `_tabs` with CRLF/indentation, `ensure_project` (needs npm),
  `record.save` atomicity. Add as needed.
- **[minor] Operational runbook for the per-section decomposition.** Who assigns a section, how to
  avoid overlap with a parallel PR, how to roll back a partially-merged large section (crm — 200+
  files).

- **[nit] Pin `actions/*` by commit SHA.** Currently by tag (`@v4`/`@v5`) + Dependabot. For strict
  supply-chain hygiene, move to SHA pinning (Dependabot supports it).
- **[minor][done] Multiple `{% list tabs %}` blocks per page.** A page can carry several
  tabs blocks — parameter-description blocks plus one or more code-example blocks (confirmed
  across the corpus during the first live run: 54 pages have ≥2 code examples, e.g.
  `user/user-get.md` has 4; the earlier "doesn't occur in the corpus" assumption was wrong).
  `_tabs.code_regions()` returns every tabs region that holds a TS code example; `validate.py`
  type-checks each example independently and `record.py` reads the method from the first one.
  Fails only when no region carries a code example. (Earlier this was a first-region-only
  scan that silently skipped examples 2..N.)
- **[nit] Forbidden tokens are matched by substring.** A legitimate comment like `// deprecated:
  callMethod` in TS/UMD will cause a FAIL. An extremely rare case (the goal is to remove traces of
  the deprecated API); if needed — forbid such comments in PROMPT.md.
- **[nit] CI cache without `restore-keys`.** Deliberately all-or-nothing; on frequent SDK bumps — a
  cold `npm ci`. Acceptable at the current scale.
