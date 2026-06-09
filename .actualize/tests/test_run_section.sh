#!/usr/bin/env bash
# Offline tests for .actualize/run-section.sh — the auto-retry layer over run-batch.sh.
# No network, no real LLM. Same approach as test_run_batch.sh: a throwaway git repo
# with the REAL run-section.sh + run-batch.sh + remaining.py / record.py / _tabs.py,
# a stub validate.py, and a stub `claude` injected via CLAUDE_BIN.
#
# The stub claude acts on the file name in the <PATH> of the prompt:
#   *pass*  -> benign edit (validates PASS)
#   *fail*  -> inject FAILVALIDATE (validates FAIL on EVERY attempt = deterministically stuck)
#   *skip*  -> no change (SKIP on every attempt = deterministically stuck)
#   *trans* -> TRANSIENT: fail the 1st attempt, pass every attempt after (per-path counter
#              file under $COUNTERDIR, which lives OUTSIDE the repo so it survives the
#              revert run-batch does on a failed file). Models the ~3% parallel miss that
#              a retry pass clears.
#
# Run: bash .actualize/tests/test_run_section.sh   (exit 0 = all passed)
set -uo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the real .actualize/
FAILS=0
ok()   { echo "ok   - $1"; }
bad()  { echo "FAIL - $1"; FAILS=$((FAILS + 1)); }
check(){ if eval "$2"; then ok "$1"; else bad "$1 [cond: $2]"; fi; }

COUNTERDIR=""   # set per-repo; transient stub counts attempts here (outside the repo)

make_repo() {
  REPO="$(mktemp -d)"
  COUNTERDIR="$(mktemp -d)"
  mkdir -p "$REPO/.actualize/tests" "$REPO/api-reference/tasks" "$REPO/bin"

  cp "$SRC_DIR/run-section.sh" "$SRC_DIR/run-batch.sh" "$SRC_DIR/remaining.py" \
     "$SRC_DIR/record.py" "$SRC_DIR/_tabs.py" "$REPO/.actualize/"
  chmod +x "$REPO/.actualize/run-section.sh" "$REPO/.actualize/run-batch.sh"
  printf 'prompt stub\n' > "$REPO/.actualize/PROMPT.md"
  printf 'date\tfile\tsha256\tstatus\tmethod\n' > "$REPO/.actualize/ledger.tsv"
  # Mirror the real repo's .actualize/.gitignore: remaining.py/record.py import _tabs.py
  # and create __pycache__/ on first use. run-section invokes run-batch repeatedly, and
  # run-batch's clean-tree gate would trip on that untracked cache between passes unless
  # it is ignored (as it is in the real tree). Without this the multi-pass tests fail.
  printf '__pycache__/\n' > "$REPO/.actualize/.gitignore"

  # stub validate.py: FAIL iff the file contains FAILVALIDATE, else PASS
  cat > "$REPO/.actualize/validate.py" <<'PY'
import sys
text = open(sys.argv[1], encoding="utf-8").read()
if "FAILVALIDATE" in text:
    print("FAIL"); sys.exit(1)
print("PASS"); sys.exit(0)
PY

  # stub claude (see header for the per-name behaviour). COUNTERDIR is read from env.
  cat > "$REPO/bin/claude" <<'SH'
#!/usr/bin/env bash
prompt=""; prev=""
for a in "$@"; do [ "$prev" = "-p" ] && prompt="$a"; prev="$a"; done
path=$(printf '%s\n' "$prompt" | grep -oE '<PATH>[^<]+</PATH>' | head -1 | sed 's/<PATH>//; s|</PATH>||')
[ -n "$path" ] || exit 0
case "$path" in
  *trans*)
    safe=$(printf '%s' "$path" | tr -c 'A-Za-z0-9._-' '_')
    cf="${COUNTERDIR:-/tmp}/$safe"
    n=$(cat "$cf" 2>/dev/null || echo 0); n=$((n + 1)); echo "$n" > "$cf"
    if [ "$n" -le 1 ]; then printf '\nFAILVALIDATE\n' >> "$path"   # 1st try fails
    else printf '\n// edited after retry\n' >> "$path"; fi          # later tries pass
    ;;
  *fail*) printf '\nFAILVALIDATE\n' >> "$path" ;;   # deterministically invalid
  *skip*) : ;;                                      # never changes
  *)      printf '\n// edited by stub\n' >> "$path" ;;
esac
exit 0
SH
  chmod +x "$REPO/bin/claude"

  # caller passes the doc base-names to create (each gets the legacy token so
  # remaining.py lists it until recorded done)
  for n in "$@"; do
    printf '# %s\n\n$b24.callMethod("x")\n' "$n" > "$REPO/api-reference/tasks/$n.md"
  done

  git -C "$REPO" init -q
  git -C "$REPO" config user.email t@t.t
  git -C "$REPO" config user.name t
  git -C "$REPO" config commit.gpgsign false
  git -C "$REPO" config tag.gpgsign false
  git -C "$REPO" add -A
  git -C "$REPO" commit -q -m init
}

# invoke the REAL run-section inside $REPO with the stub claude on PATH
section() {  # args: extra env assignments are already in the caller's environment
  ( cd "$REPO" && PATH="$REPO/bin:$PATH" COUNTERDIR="$COUNTERDIR" CLAUDE_BIN=claude \
      "$@" bash .actualize/run-section.sh api-reference/tasks 10 2 )
}
remaining_n() {  # current "remaining" count for the tasks root in $REPO
  ( cd "$REPO" && python3 .actualize/remaining.py api-reference/tasks 2>/dev/null \
      | grep -oE 'not done\): [0-9]+' | grep -oE '[0-9]+$' )
}

# ============================ scenarios =======================================

# 1) DRY RUN: no RUN -> delegates to run-batch dry plan, exit 0, changes nothing
make_repo pass1 pass2
out="$(section)"; rc=$?
check "dry-run exit 0"                  "[ $rc -eq 0 ]"
check "dry-run shows run-section banner" "printf '%s' \"\$out\" | grep -q 'run-section DRY RUN'"
check "dry-run shows run-batch plan"     "printf '%s' \"\$out\" | grep -q 'batch plan'"
check "dry-run leaves tree clean"        "[ -z \"\$(git -C \"\$REPO\" status --porcelain)\" ]"
check "dry-run records nothing"          "! grep -qE 'pass1|pass2' \"\$REPO/.actualize/ledger.tsv\""
rm -rf "$REPO" "$COUNTERDIR"

# 2) ALL-PASS: RUN=1 drains everything in the parallel phase, exit 0
make_repo pass1 pass2 pass3
out="$( RUN=1 section 2>&1 )"; rc=$?
check "all-pass exit 0"                  "[ $rc -eq 0 ]"
check "all-pass drained in parallel"     "printf '%s' \"\$out\" | grep -q 'fully drained in the parallel phase'"
check "all-pass remaining 0"             "[ \"\$(remaining_n)\" = 0 ]"
check "all-pass: pass1 recorded"         "grep -q 'pass1.md' \"\$REPO/.actualize/ledger.tsv\""
check "all-pass: pass3 recorded"         "grep -q 'pass3.md' \"\$REPO/.actualize/ledger.tsv\""
rm -rf "$REPO" "$COUNTERDIR"

# 3) TRANSIENT auto-retry: a file that fails its 1st attempt is docatched by a later
#    pass (the whole point of run-section). Ends fully drained, exit 0.
make_repo pass1 trans1 trans2
out="$( RUN=1 section 2>&1 )"; rc=$?
check "transient run exit 0"             "[ $rc -eq 0 ]"
check "transient fully drained"          "[ \"\$(remaining_n)\" = 0 ]"
check "transient: trans1 recorded done"  "grep -q 'trans1.md' \"\$REPO/.actualize/ledger.tsv\""
check "transient: trans2 recorded done"  "grep -q 'trans2.md' \"\$REPO/.actualize/ledger.tsv\""
check "transient: no FAILVALIDATE left"  "! grep -rq 'FAILVALIDATE' \"\$REPO/api-reference/tasks\""
rm -rf "$REPO" "$COUNTERDIR"

# 4) STUCK does not spin: a deterministically-failing file ends the run with exit 2
#    (drained as far as possible), passes/transients still completed, and it must
#    TERMINATE (the plateau guard) rather than loop forever.
make_repo pass1 trans1 fail1
out="$( RUN=1 MAX_PASSES=8 timeout 60 bash -c '
          cd "'"$REPO"'" && PATH="'"$REPO"'/bin:$PATH" COUNTERDIR="'"$COUNTERDIR"'" \
          CLAUDE_BIN=claude RUN=1 MAX_PASSES=8 \
          bash .actualize/run-section.sh api-reference/tasks 10 2' 2>&1 )"; rc=$?
check "stuck terminates (not 124 timeout)" "[ $rc -ne 124 ]"
check "stuck exits 2"                      "[ $rc -eq 2 ]"
check "stuck reports STUCK"                "printf '%s' \"\$out\" | grep -q 'STUCK'"
check "stuck: pass1 still completed"       "grep -q 'pass1.md' \"\$REPO/.actualize/ledger.tsv\""
check "stuck: trans1 still docatched"      "grep -q 'trans1.md' \"\$REPO/.actualize/ledger.tsv\""
check "stuck: fail1 NOT recorded"          "! grep -q 'fail1.md' \"\$REPO/.actualize/ledger.tsv\""
check "stuck: 1 file remains"              "[ \"\$(remaining_n)\" = 1 ]"
check "stuck: reached sequential phase"    "printf '%s' \"\$out\" | grep -q 'sequential mop-up'"
rm -rf "$REPO" "$COUNTERDIR"

# 5) HARD-ABORT passthrough: a dirty tree makes run-batch refuse (exit 1); run-section
#    must surface that verbatim and NOT enter a retry loop.
make_repo pass1
echo dirty >> "$REPO/api-reference/tasks/pass1.md"
out="$( RUN=1 section 2>&1 )"; rc=$?
check "dirty tree: exit 1 (passthrough)"   "[ $rc -eq 1 ]"
check "dirty tree: run-batch message shown" "printf '%s' \"\$out\" | grep -qi 'not clean'"
rm -rf "$REPO" "$COUNTERDIR"

echo
if [ "$FAILS" -eq 0 ]; then echo "ALL run-section TESTS PASSED"; exit 0
else echo "$FAILS run-section TEST(S) FAILED"; exit 1; fi
