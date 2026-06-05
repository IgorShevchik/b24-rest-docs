# .actualize — b24jssdk JS-example actualization process

Tooling for replacing deprecated jsSDK examples (`$b24.callMethod` / `callListMethod` /
`fetchListMethod`) with current **TS** and **UMD** tabs built on `@bitrix24/b24jssdk` (the
actions API). The actions API already ships in the current `@1`, and the old methods are
deprecated (removed in 2.0). This is an internal process folder — it can be left out of
documentation PRs.

## Files

| File | Purpose |
|------|---------|
| `PROMPT.md` | Prompt for actualizing **one file**. Orchestration via `run-batch.sh` or by hand (`remaining.py --list`). |
| `PROMPT-REVIEW.md` | Second prompt: review of an already-actualized file. |
| `validate.py` | Tab structure + forbidden tokens + `tsc --strict` (lockfile-pinned) + `node --check`. Optional `--project DIR` — the typecheck sandbox dir (default `.actualize/.tscheck`). |
| `record.py` | Idempotent `ledger.tsv` journal (upsert, atomic write); `--verify-all` / `--verify <path>` — sha256 drift control. |
| `remaining.py` | How many files are still unprocessed (and the list). |
| `run-batch.sh` | Batch orchestrator over the three scripts: edits files with the agent (in parallel), validates and writes the ledger (serially), commits the ones that pass. **Dry-run by default** (needs `RUN=1`); ⚠️ EXPERIMENTAL — not yet exercised by a real run. Requires GNU bash ≥ 4. |
| `_tabs.py` | Shared tab-parsing regexes (used by `validate.py` and `record.py`). A page may have several `{% list tabs %}` blocks; `code_regions()` returns every region holding a TS example, so each one is validated. |
| `ledger.tsv` | Journal: date, file, sha256, status, method (empty in the tooling PR). |
| `typecheck/` | Pinned typecheck environment (`package.json` + `package-lock.json`). |
| `tests/` | Offline tooling unit tests (`python -m unittest discover -s .actualize/tests`). |

## How to run

```bash
# what's left
python3 .actualize/remaining.py api-reference                 # counter
python3 .actualize/remaining.py api-reference/tasks --list    # list

# actualize a file per PROMPT.md (LLM agent), then validate and record:
python3 .actualize/validate.py api-reference/tasks/tasks-task-get.md   # -> PASS
python3 .actualize/record.py   api-reference/tasks/tasks-task-get.md done

# (optional) review per PROMPT-REVIEW.md:
python3 .actualize/record.py   api-reference/tasks/tasks-task-get.md reviewed

# drift control after edits
python3 .actualize/record.py --verify-all                                     # all
python3 .actualize/record.py --verify api-reference/tasks/tasks-task-get.md   # one file

# offline tooling tests (no network)
python -m unittest discover -s .actualize/tests -p 'test_*.py'
```

The first `validate.py` run installs the dependencies from the committed
`.actualize/typecheck/package-lock.json` (via `npm ci --ignore-scripts`) into
`.actualize/.tscheck/` (which is `.gitignore`d). The example UMD tag is the major tag `@1`;
the typecheck is pinned by the lockfile (a specific 1.x). **Bumping the SDK version:** update
`.actualize/typecheck/package.json` + `package-lock.json` and re-run `validate.py` over the
`done` files.

### Bulk run (batch-runner)

> ⚠️ **EXPERIMENTAL.** The script is checked syntactically, in dry-run, and by the offline
> harness (`tests/test_run_batch.sh`), but has not yet been exercised by a real `RUN=1` run
> over the corpus. Do the first real run small (`N=3 PAR=1`) on a throwaway branch under
> supervision. Requires **GNU bash ≥ 4** (macOS ships bash 3.2 by default — install a newer
> one or use Linux).

`run-batch.sh` runs the "agent → blast-radius check → `validate.py` → `record.py`" chain in
batches: the edit step runs in parallel (`xargs -0 -P`, files are distinct), then the
blast-radius check, then validation and ledger writes run serially (a single writer, no race).
Passing files are committed; failing ones are reverted and stay in `remaining` for the next
pass.

**Dry-run by default.** Without `RUN=1` the script only prints the plan (which files it would
touch) and exits — it changes nothing and commits nothing. This is a guard: the script `cd`s to
the repo root itself, so an accidental run must not silently change files. Additionally, with
`RUN=1` the script **refuses to start on a dirty working tree** — so a batch can commit only its
own edits and never mixes in unrelated changes. Run it from a branch for **documentation** edits,
not from the tooling PR (on `main`/`master` the script warns). Before starting it checks the agent
binary is present (`CLAUDE_BIN`).

**Prompt-injection guard (blast-radius check).** The `.md` content fed to the agent is untrusted
data: a system preamble forbids touching anything but `<PATH>`. But the main protection is **not
trust in the model**: after the edit phase the script compares the actually-changed files (tracked
+ untracked) against the batch plan. Anything outside the plan (a neighbouring file, a new
untracked file, a secret written out) → **the whole batch is reverted, nothing is committed**
(`SECURITY ABORT`). So an injection that made the agent write outside `<PATH>` cannot smuggle
anything into a commit. **Limitation:** this is a working-tree check (`git status`), so it does not
catch what git does not show: writes **outside the repository** (an absolute path — `~/.ssh`,
`/tmp`), **gitignored paths in the tree** (`.claude/`, `CLAUDE.md`), and **`.git/`** (e.g.
`.git/config`). Closing this fully needs process-level FS sandboxing of the agent
(bubblewrap/firejail or an `--add-dir` allowlist) — see `FOLLOWUPS.md`.

```bash
# plan with no changes (dry-run): ROOT, N (files per batch, 0 = all), PAR (parallel edits)
.actualize/run-batch.sh api-reference/tasks 20 4

# real run of one batch (requires a clean tree):
RUN=1 .actualize/run-batch.sh api-reference/tasks 20 4

# grind a section to zero (resumable via the ledger; `|| break` catches both an error and
# "no progress": exit 3 when all remaining files keep SKIP/FAIL):
while python3 .actualize/remaining.py api-reference/tasks --limit 1 \
        | grep -q 'not done): [1-9]'; do
  RUN=1 .actualize/run-batch.sh api-reference/tasks 30 4 || break
done
```

Toggles: `RUN=1` (real run), `EDIT_TIMEOUT` (seconds per file, default 600, needs `timeout` on
PATH), `KEEP_FAILED=1` (do not revert failures + keep logs), `NO_COMMIT=1` (do not commit),
`CLAUDE_MODEL`, `CLAUDE_BIN` (agent binary, for tests). The batch result prints as
`batch summary: PASSED=… FAILED=… SKIPPED=…`. Edit/validation logs go to a temp dir (`mktemp -d`,
printed at start; removed at the end — except with `KEEP_FAILED=1`, on `SECURITY ABORT`, and on
Ctrl-C, when the dir is kept for diagnostics) and never land in a commit.

**SKIP is normal.** If the agent did not change a file (no `- JS` tab, or a `SKIP` reply), the
file is not written to the ledger and stays in `remaining` — repeated SKIPs in the logs are
expected.

**Interruption (Ctrl-C).** During the edit phase — safe (nothing is committed yet). During the
validation/write phase — the tree may keep edits and/or ledger rows that were written but not
committed; the script prints a hint — check `git status` and either commit or revert.

**Note:** `validate.py` is a structural gate (tabs, tokens, `tsc`, `node --check`) plus a field/method
cross-check that grounds the result type in the page (the `method:` must match the cURL endpoint, and
result-type field names must appear in a JSON example or a `|| **field** ||` table). It still does
**not** check value semantics (choosing `v2`/`v3`, field types/nesting, business logic) — run a sample
through `PROMPT-REVIEW.md` and mark it `reviewed`.

**Ledger and merge order.** Tooling and documentation edits go in separate PRs; the tooling PR is
merged **first**. `ledger.tsv` is empty in the tooling PR (header only) — rows are added as files
are processed (together with their content), otherwise `--verify-all` on `main` would show drift
before the docs land. `ledger.tsv` conflicts across parallel PRs are absorbed by `merge=union`
(`.actualize/.gitattributes`) + the idempotent upsert (`load()` also dedups rows per file on read).

## Decisions (recorded in PROMPT.md)

- Instead of a single `JS` tab → two tabs **JS (TS)** (assumes a ready `$b24`) and **JS (UMD)**
  (full initialization via `B24Js.initializeB24Frame()`) — the doc-team tab-naming convention.
- Response handling: `try/catch` + an `response.isSuccess` check; in TS — `getData()!`, in UMD —
  `getData()`; for lists — `result.<key>.length` (`getTotal()` is deprecated / removed in 2.0).
- `requestId` is generated by the SDK: `Text.getUuidRfc4122()` (TS, `import { Text }`) /
  `B24Js.Text.getUuidRfc4122()` (UMD).
- TS header: explanatory comments (ES module, `$b24`) come first; the type is imported as
  `import type { B24Frame[, ISODate] }`; date fields in the result type are `ISODate | null`.
- Comments and string values are in English (the SDK targets international developers). The
  PHP/BX24.js/cURL tabs stay as they are, including Russian comments and pre-existing
  `processData()` — that is out of scope.
- Version: `actions.v2` by default; `actions.v3` for `rest-v3/**` and `result.item` responses.
- List methods: a single variant — `call.make` with `start` (preserves `order`). Above
  `const response`, a hint about both helpers `callList.make` / `fetchList.make` with a `NOTE` that
  they do NOT accept `order` (excluded from their type — a `tsc` error if passed).

## Deferred items

Strategic tasks (SDK version policy, batch-runner improvements) are in
[`FOLLOWUPS.md`](FOLLOWUPS.md) (GitHub Issues are disabled in the repository).

---
_Last reviewed: 2026-06-04_
