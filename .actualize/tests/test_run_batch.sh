#!/usr/bin/env bash
# Offline tests for .actualize/run-batch.sh — no network, no real LLM agent.
#
# Strategy: build a throwaway git repo containing the REAL run-batch.sh plus the
# real remaining.py / record.py / _tabs.py (all stdlib, offline). Only validate.py
# is replaced by a stub (the real one runs tsc/npm and needs network), and the LLM
# agent is a stub `claude` injected via the CLAUDE_BIN seam. This exercises the real
# bash orchestration: dry-run gate, numeric/clean-tree guards, and the
# PASS / FAIL(+revert) / SKIP branches plus commit scoping.
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
  cat > "$REPO/bin/claude" <<'SH'
#!/usr/bin/env bash
prompt=""; prev=""
for a in "$@"; do [ "$prev" = "-p" ] && prompt="$a"; prev="$a"; done
path=$(printf '%s\n' "$prompt" | grep -oE '<PATH>[^<]+</PATH>' | head -1 | sed 's/<PATH>//; s|</PATH>||')
[ -n "$path" ] || exit 0
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

# ============================ result ==========================================
echo "----"
if [ "$FAILS" -eq 0 ]; then echo "ALL run-batch.sh TESTS PASSED"; exit 0
else echo "$FAILS run-batch.sh test(s) FAILED"; exit 1; fi
