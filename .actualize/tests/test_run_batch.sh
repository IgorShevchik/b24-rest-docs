#!/usr/bin/env bash
# Offline tests for .actualize/run-batch.sh — no network, no real LLM agent.
#
# Strategy: build a throwaway git repo containing the REAL run-batch.sh plus the
# real remaining.py / record.py / _tabs.py (all stdlib, offline). Only validate.py
# is replaced by a stub (the real one runs tsc/npm and needs network), and the LLM
# agent is a stub `claude` injected via the CLAUDE_BIN seam. This exercises the real
# bash orchestration: dry-run gate, numeric/clean-tree guards, the PASS / FAIL(+revert)
# / SKIP branches, commit scoping, blast-radius abort, and the negative paths
# (record-fail, KEEP_FAILED, commit-fail, no-progress exit, gitignored blind spot).
#
# Run: bash .actualize/tests/test_run_batch.sh   (exit 0 = all passed)
set -uo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the real .actualize/
FAILS=0
ok()   { echo "ok   - $1"; }
bad()  { echo "FAIL - $1"; FAILS=$((FAILS + 1)); }
check(){ if eval "$2"; then ok "$1"; else bad "$1 [cond: $2]"; fi; }

# --- build a fresh fake repo, return its path via $REPO ------------------------
make_repo() {
  REPO="$(mktemp -d)"
  mkdir -p "$REPO/.actualize" "$REPO/api-reference/tasks" "$REPO/bin"

  # real helpers (offline-safe)
  cp "$SRC_DIR/run-batch.sh" "$SRC_DIR/remaining.py" "$SRC_DIR/record.py" \
     "$SRC_DIR/_tabs.py" "$REPO/.actualize/"
  printf 'prompt stub\n' > "$REPO/.actualize/PROMPT.md"
  printf 'date\tfile\tsha256\tstatus\tmethod\n' > "$REPO/.actualize/ledger.tsv"

  # stub validate.py: FAIL iff the file contains FAILVALIDATE, else PASS
  cat > "$REPO/.actualize/validate.py" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
if "FAILVALIDATE" in text:
    print("FAIL"); sys.exit(1)
print("PASS"); sys.exit(0)
PY

  # stub claude: parse <PATH> from the -p prompt, then act on the file name:
  #   *skip*  -> leave unchanged (SKIP)        *fail* -> inject FAILVALIDATE (FAIL)
  #   else    -> append a benign edit (PASS)
  # If STUB_ESCAPE_FILE is set, the stub ALSO writes to that path — simulating a
  # prompt-injected agent stepping outside its lane (for the blast-radius test).
  cat > "$REPO/bin/claude" <<'SH'
#!/usr/bin/env bash
prompt=""; prev=""
for a in "$@"; do [ "$prev" = "-p" ] && prompt="$a"; prev="$a"; done
path=$(printf '%s\n' "$prompt" | grep -oE '<PATH>[^<]+</PATH>' | head -1 | sed 's/<PATH>//; s|</PATH>||')
[ -n "$path" ] || exit 0
[ -n "${STUB_ESCAPE_FILE:-}" ] && printf 'pwned\n' >> "$STUB_ESCAPE_FILE"
case "$path" in
  *skip*) : ;;                                   # no change
  *fail*) printf '\nFAILVALIDATE\n' >> "$path" ;;
  *)      printf '\n// edited by stub\n' >> "$path" ;;
esac
exit 0
SH
  chmod +x "$REPO/bin/claude"

  # test docs: each must carry the legacy token so the real remaining.py lists it
  for n in pass1 pass2 skip1 fail1; do
    printf '# %s\n\n$b24.callMethod("x")\n' "$n" > "$REPO/api-reference/tasks/$n.md"
  done

  git -C "$REPO" init -q
  git -C "$REPO" config user.email t@t.t
  git -C "$REPO" config user.name t
  git -C "$REPO" config commit.gpgsign false   # don't depend on the host signing setup
  git -C "$REPO" config tag.gpgsign false
  git -C "$REPO" add -A
  git -C "$REPO" commit -q -m init
}

run() {  # run the real script inside $REPO with stub claude on PATH
  ( cd "$REPO" && PATH="$REPO/bin:$PATH" CLAUDE_BIN=claude "$@" \
      bash .actualize/run-batch.sh api-reference/tasks 10 2 )
}

# ============================ scenarios =======================================

# 1) DRY RUN: no RUN -> exits 0, prints plan, changes nothing
make_repo
out="$(run)"; rc=$?
check "dry-run exit 0"                 "[ $rc -eq 0 ]"
check "dry-run prints DRY RUN"         "printf '%s' \"\$out\" | grep -q 'DRY RUN'"
check "dry-run leaves tree clean"      "[ -z \"\$(git -C \"\$REPO\" status --porcelain)\" ]"
rm -rf "$REPO"

# 2) numeric-arg guard: N not a number -> exit 2
make_repo
( cd "$REPO" && bash .actualize/run-batch.sh api-reference/tasks notanum 2 ) >/dev/null 2>&1; rc=$?
check "non-numeric N exits 2"          "[ $rc -eq 2 ]"
rm -rf "$REPO"

# 3) clean-tree precondition: RUN=1 on dirty tree -> refuses (exit 1)
make_repo
echo dirty >> "$REPO/api-reference/tasks/pass1.md"
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "dirty tree refused (exit 1)"    "[ $rc -eq 1 ]"
check "dirty refusal message"          "printf '%s' \"\$out\" | grep -qi 'not clean'"
rm -rf "$REPO"

# 4) RUN=1 NO_COMMIT: pass edited+recorded, skip untouched, fail reverted, summary
make_repo
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "run exit 0"                     "[ $rc -eq 0 ]"
check "summary PASSED=2"               "printf '%s' \"\$out\" | grep -q 'PASSED=2'"
check "summary FAILED=1"               "printf '%s' \"\$out\" | grep -q 'FAILED=1'"
check "summary SKIPPED=1"              "printf '%s' \"\$out\" | grep -q 'SKIPPED=1'"
check "pass1 recorded in ledger"       "grep -q 'pass1.md' \"\$REPO/.actualize/ledger.tsv\""
check "pass2 recorded in ledger"       "grep -q 'pass2.md' \"\$REPO/.actualize/ledger.tsv\""
check "fail1 NOT recorded"             "! grep -q 'fail1.md' \"\$REPO/.actualize/ledger.tsv\""
check "fail1 reverted (no marker)"     "! grep -q 'FAILVALIDATE' \"\$REPO/api-reference/tasks/fail1.md\""
check "NO_COMMIT made no commit"       "[ \"\$(git -C \"\$REPO\" rev-list --count HEAD)\" -eq 1 ]"
check "NO_COMMIT leaves tree dirty"    "[ -n \"\$(git -C \"\$REPO\" status --porcelain)\" ]"
check "NO_COMMIT: pass1 left in tree"  "git -C \"\$REPO\" status --porcelain | grep -q 'pass1.md'"
rm -rf "$REPO"

# 5) RUN=1 with commit: exactly pass files + ledger committed (scope, not -A)
make_repo
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "commit run exit 0"              "[ $rc -eq 0 ]"
check "exactly one new commit"         "[ \"\$(git -C \"\$REPO\" rev-list --count HEAD)\" -eq 2 ]"
files="$(git -C "$REPO" show --stat --format= HEAD | grep -oE 'api-reference/tasks/[a-z0-9]+\.md|ledger\.tsv' | sort -u)"
check "commit has pass1"               "printf '%s' \"\$files\" | grep -q 'pass1.md'"
check "commit has pass2"               "printf '%s' \"\$files\" | grep -q 'pass2.md'"
check "commit has ledger"              "printf '%s' \"\$files\" | grep -q 'ledger.tsv'"
check "commit excludes fail1 (scope)"  "! printf '%s' \"\$files\" | grep -q 'fail1.md'"
check "commit excludes skip1 (scope)"  "! printf '%s' \"\$files\" | grep -q 'skip1.md'"
rm -rf "$REPO"

# 6) BLAST-RADIUS: agent writes OUTSIDE the plan -> abort, revert, nothing committed
make_repo
# the stub will also scribble into a sibling file not in the batch plan
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 \
        STUB_ESCAPE_FILE="$REPO/api-reference/tasks/INJECTED.md" \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "escape aborts (exit 1)"         "[ $rc -eq 1 ]"
check "escape prints SECURITY ABORT"   "printf '%s' \"\$out\" | grep -q 'SECURITY ABORT'"
check "escape names the stray file"    "printf '%s' \"\$out\" | grep -q 'INJECTED.md'"
check "no commit after escape"         "[ \"\$(git -C \"\$REPO\" rev-list --count HEAD)\" -eq 1 ]"
check "planned edits reverted"         "[ -z \"\$(git -C \"\$REPO\" status --porcelain)\" ]"
check "stray untracked file removed"   "[ ! -f \"\$REPO/api-reference/tasks/INJECTED.md\" ]"
check "nothing recorded in ledger"     "! grep -qE 'pass1|pass2' \"\$REPO/.actualize/ledger.tsv\""
rm -rf "$REPO"

# 7) KNOWN LIMITATION (documentation test): blast-radius is a WORKING-TREE check, so
#    a write OUTSIDE the repo (an absolute path like ~/.ssh or /tmp) is NOT caught.
#    This pins that gap: the batch proceeds normally and the out-of-tree file IS
#    created. If a future change adds process-level FS sandboxing that DOES catch it,
#    this test will fail — that is the reminder to update the docs / FOLLOWUPS.
make_repo
ESC_DIR="$(mktemp -d)"; ESC="$ESC_DIR/escape.txt"     # a path OUTSIDE the fake repo
check "test7 self-guard: ESC_DIR != REPO"             "[ \"\$ESC_DIR\" != \"\$REPO\" ]"
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        STUB_ESCAPE_FILE="$ESC" \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "out-of-tree write does NOT abort (exit 0)"     "[ $rc -eq 0 ]"
check "out-of-tree write not flagged SECURITY ABORT"  "! printf '%s' \"\$out\" | grep -q 'SECURITY ABORT'"
check "KNOWN LIMITATION: out-of-tree file created"    "[ -f \"\$ESC\" ]"
rm -rf "$REPO" "$ESC_DIR"

# 8) gitignored IN-TREE escape is now CAUGHT: ls-files --others (without --exclude-standard)
#    surfaces a NEW gitignored write, so the blast-radius check aborts, reverts and removes it.
make_repo
printf 'secret-drop/\n' > "$REPO/.gitignore"
git -C "$REPO" add .gitignore && git -C "$REPO" commit -q -m "add gitignore" >/dev/null
mkdir -p "$REPO/secret-drop"
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        STUB_ESCAPE_FILE="$REPO/secret-drop/loot.txt" \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "gitignored escape aborts (exit 1)"          "[ $rc -eq 1 ]"
check "gitignored escape flagged SECURITY ABORT"   "printf '%s' \"\$out\" | grep -q 'SECURITY ABORT'"
check "gitignored escape names loot file"          "printf '%s' \"\$out\" | grep -q 'loot.txt'"
check "gitignored loot removed"                    "[ ! -f \"\$REPO/secret-drop/loot.txt\" ]"
rm -rf "$REPO"

# 8b) a developer's PRE-EXISTING gitignored file must NOT be mistaken for agent loot (the
#     IGNORED_BEFORE snapshot), so a normal run with a local .env present proceeds untouched.
make_repo
printf 'localcfg/\n' > "$REPO/.gitignore"
git -C "$REPO" add .gitignore && git -C "$REPO" commit -q -m gi >/dev/null
mkdir -p "$REPO/localcfg"; printf 'dev secret\n' > "$REPO/localcfg/.env"   # exists BEFORE the run
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "pre-existing ignored file: no abort (exit 0)" "[ $rc -eq 0 ]"
check "pre-existing ignored file: not flagged"       "! printf '%s' \"\$out\" | grep -q 'SECURITY ABORT'"
check "pre-existing ignored file: left untouched"    "[ -f \"\$REPO/localcfg/.env\" ]"
rm -rf "$REPO"

# 9) record.py failure -> validated file reverted, not recorded, tree stays clean
make_repo
printf 'import sys; sys.exit(1)\n' > "$REPO/.actualize/record.py"   # force record to fail
git -C "$REPO" commit -q -am "stub record.py to fail" >/dev/null
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "record-fail: mentions record.py failed"  "printf '%s' \"\$out\" | grep -q 'record.py failed'"
check "record-fail: tree clean (reverted)"      "[ -z \"\$(git -C \"\$REPO\" status --porcelain)\" ]"
check "record-fail: nothing added to ledger"    "[ \"\$(wc -l < \"\$REPO/.actualize/ledger.tsv\")\" -eq 1 ]"
rm -rf "$REPO"

# 10) KEEP_FAILED=1 -> a validate-FAILED file is left in the tree (not reverted)
make_repo
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 KEEP_FAILED=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "KEEP_FAILED: fail1 left dirty"        "git -C \"\$REPO\" status --porcelain | grep -q 'fail1.md'"
check "KEEP_FAILED: FAILVALIDATE remains"    "grep -q 'FAILVALIDATE' \"\$REPO/api-reference/tasks/fail1.md\""
check "KEEP_FAILED: summary FAILED=1"        "printf '%s' \"\$out\" | grep -q 'FAILED=1'"
rm -rf "$REPO"

# 11) git commit failure (pre-commit hook) -> exit 1 + recovery hint; ledger already written
make_repo
mkdir -p "$REPO/.git/hooks"
printf '#!/bin/sh\nexit 1\n' > "$REPO/.git/hooks/pre-commit"; chmod +x "$REPO/.git/hooks/pre-commit"
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "commit-fail: exit 1"              "[ $rc -eq 1 ]"
check "commit-fail: COMMIT FAILED hint"  "printf '%s' \"\$out\" | grep -q 'COMMIT FAILED'"
check "commit-fail: ledger has pass1"    "grep -q 'pass1.md' \"\$REPO/.actualize/ledger.tsv\""
check "commit-fail: no new commit"       "[ \"\$(git -C \"\$REPO\" rev-list --count HEAD)\" -eq 1 ]"
rm -rf "$REPO"

# 12) no progress (all remaining files SKIP) -> exit 3 so a `... || break` drain loop stops
make_repo
git -C "$REPO" rm -q api-reference/tasks/pass1.md api-reference/tasks/pass2.md api-reference/tasks/fail1.md >/dev/null
git -C "$REPO" commit -q -m "leave only skip1" >/dev/null
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "all-skip: exit 3 (no progress)"   "[ $rc -eq 3 ]"
check "all-skip: prints 'no progress'"   "printf '%s' \"\$out\" | grep -q 'no progress'"
check "all-skip: summary PASSED=0"       "printf '%s' \"\$out\" | grep -q 'PASSED=0'"
rm -rf "$REPO"

# 13) missing agent binary under RUN=1 -> fail fast (exit 1) before any edit/commit
make_repo
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 CLAUDE_BIN=definitely-not-a-real-binary-xyz \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "missing binary: exit 1"           "[ $rc -eq 1 ]"
check "missing binary: clear message"    "printf '%s' \"\$out\" | grep -q 'agent binary not found'"
check "missing binary: no commit"        "[ \"\$(git -C \"\$REPO\" rev-list --count HEAD)\" -eq 1 ]"
rm -rf "$REPO"

# 14) default-branch guard: warns on master/main, silent on a docs branch (soft, non-blocking)
make_repo
git -C "$REPO" checkout -q -B master
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"
check "master: branch warning shown"     "printf '%s' \"\$out\" | grep -q 'WARNING: on'"
rm -rf "$REPO"
make_repo
git -C "$REPO" checkout -q -B docs/feature
out="$( cd "$REPO" && PATH="$REPO/bin:$PATH" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"
check "docs branch: no branch warning"   "! printf '%s' \"\$out\" | grep -q 'WARNING: on'"
rm -rf "$REPO"

# 15) CLI preflight: a CLAUDE_BIN whose --help omits the driven flags fails fast (exit 1).
#     The stub lives OUTSIDE the repo (absolute CLAUDE_BIN) so the tree stays clean.
make_repo
STUB="$(mktemp)"
cat > "$STUB" <<'SH'
#!/usr/bin/env bash
[ "$1" = "--help" ] && { echo "usage: claude -p PROMPT [--model M]"; exit 0; }   # advertises no flags
exit 0
SH
chmod +x "$STUB"
out="$( cd "$REPO" && CLAUDE_BIN="$STUB" RUN=1 NO_COMMIT=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "preflight: incompatible CLI exits 1"      "[ $rc -eq 1 ]"
check "preflight: names the missing capability"  "printf '%s' \"\$out\" | grep -q 'does not advertise'"
rm -rf "$REPO"; rm -f "$STUB"

# 16) secret-scan: an AWS-key-shaped string injected by the agent blocks the commit (exit 1).
#     External stub (absolute CLAUDE_BIN) keeps the tree clean; commit count is checked vs baseline.
make_repo
STUB="$(mktemp)"
cat > "$STUB" <<'SH'
#!/usr/bin/env bash
prompt=""; prev=""
for a in "$@"; do [ "$prev" = "-p" ] && prompt="$a"; prev="$a"; done
[ "$1" = "--help" ] && { echo "--permission-mode --allowed-tools"; exit 0; }
path=$(printf '%s\n' "$prompt" | grep -oE '<PATH>[^<]+</PATH>' | head -1 | sed 's/<PATH>//; s|</PATH>||')
[ -n "$path" ] || exit 0
case "$path" in
  *pass1*) printf '\n// AKIAIOSFODNN7EXAMPLE\n' >> "$path" ;;   # AWS-access-key-shaped string
  *)       printf '\n// edited by stub\n' >> "$path" ;;
esac
exit 0
SH
chmod +x "$STUB"
base=$(git -C "$REPO" rev-list --count HEAD)
out="$( cd "$REPO" && CLAUDE_BIN="$STUB" RUN=1 \
        bash .actualize/run-batch.sh api-reference/tasks 10 2 2>&1 )"; rc=$?
check "secret-scan: aborts the commit (exit 1)"  "[ $rc -eq 1 ]"
check "secret-scan: flags possible secret"       "printf '%s' \"\$out\" | grep -q 'possible secret'"
check "secret-scan: no new commit"               "[ \"\$(git -C \"\$REPO\" rev-list --count HEAD)\" -eq $base ]"
rm -rf "$REPO"; rm -f "$STUB"

# ============================ result ==========================================
echo "----"
if [ "$FAILS" -eq 0 ]; then echo "ALL run-batch.sh TESTS PASSED"; exit 0
else echo "$FAILS run-batch.sh test(s) FAILED"; exit 1; fi
