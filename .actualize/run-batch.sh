#!/usr/bin/env bash
# .actualize/run-batch.sh — orchestrator for mass actualization, layered over the
# existing scripts (remaining.py / validate.py / record.py). It does NOT change
# their contracts; it only drives them.
#
# SAFETY: dry-run by default. Without RUN=1 it prints the batch plan (the files it
# WOULD touch) and exits without editing, validating, or committing anything. Pass
# RUN=1 to actually do the work. (This guard exists because the script cd's to the
# repo root on start, so an accidental invocation must not silently mutate files.)
#
# One run = one batch: edit files via agent (parallel) -> validate + write ledger
# (serial) -> commit the passed ones (checkpoint). Resumable for free: remaining.py
# skips files already recorded in the ledger, so a re-run continues from the
# remainder, and a retry is just the next run. Ctrl-C is safe — done files are
# already committed; an in-flight edit is reverted on the next validate pass.
#
# Usage:
#   .actualize/run-batch.sh [ROOT] [N] [PAR]         # DRY RUN (plan only)
#   RUN=1 .actualize/run-batch.sh [ROOT] [N] [PAR]   # actually run
#     ROOT  walk directory             (default: api-reference/tasks)
#     N     files per batch, 0 = all   (default: 20)  — checkpoint granularity
#     PAR   parallel agent edits       (default: 4)
#
# Env toggles:
#   RUN=1             actually edit/validate/commit (omit => dry run)
#   EDIT_TIMEOUT=600  seconds per file for the agent edit (needs `timeout`)
#   KEEP_FAILED=1     do not revert failed edits (leave them for manual inspection)
#   NO_COMMIT=1       validate + record into the ledger, but do not git-commit
#   CLAUDE_MODEL=...  passed through to `claude --model`
#
# Drain a section to zero (each run is resumable through the ledger):
#   while python3 .actualize/remaining.py api-reference/tasks --limit 1 \
#           | grep -q 'not done): [1-9]'; do
#     RUN=1 .actualize/run-batch.sh api-reference/tasks 30 4 || break
#   done
set -uo pipefail   # NOT -e: per-file failures are handled; one bad file != batch abort

cd "$(dirname "$0")/.." || { echo "cannot cd to repo root" >&2; exit 1; }
[ -f .actualize/remaining.py ] || { echo "run from the b24-rest-docs repo" >&2; exit 1; }

ROOT="${1:-api-reference/tasks}"
N="${2:-20}"
PAR="${3:-4}"

# --- 0. remainder list (remaining.py is already ledger-aware) ------------------
# N=0 -> --list (all); otherwise --limit N. Keep only path lines (*.md).
if [ "$N" -eq 0 ]; then LIST_ARGS=(--list); else LIST_ARGS=(--limit "$N"); fi
mapfile -t FILES < <(python3 .actualize/remaining.py "$ROOT" "${LIST_ARGS[@]}" | grep -E '\.md$')
if [ "${#FILES[@]}" -eq 0 ]; then
  echo ">> nothing remaining under $ROOT — done."
  exit 0
fi

echo ">> batch plan: ${#FILES[@]} file(s) under $ROOT  (par=$PAR)"
printf '   %s\n' "${FILES[@]}"

# --- dry-run gate: do nothing unless explicitly told to run -------------------
if [ "${RUN:-0}" != "1" ]; then
  echo ">> DRY RUN — set RUN=1 to edit + validate + commit. Nothing changed."
  exit 0
fi

if [ ! -d .actualize/.tscheck/node_modules ]; then
  echo ">> note: first validate.py runs 'npm ci' (lockfile-pinned toolchain) — needs network."
fi

LOGDIR="$(mktemp -d)"          # logs live outside the repo => never get committed
export LOGDIR
echo ">> logs: $LOGDIR"

# --- 1. EDIT — parallel (slow step; files differ => no working-tree conflict) --
edit_one() {
  f="$1"
  log="$LOGDIR/$(printf '%s' "$f" | tr '/' '_').edit.log"
  prompt="$(cat .actualize/PROMPT.md)

<PATH>$f</PATH>
Actualize ONLY the file at the path above following the prompt, then stop."
  model_args=()
  [ -n "${CLAUDE_MODEL:-}" ] && model_args=(--model "$CLAUDE_MODEL")
  if command -v timeout >/dev/null 2>&1; then
    timeout "${EDIT_TIMEOUT:-600}" \
      claude -p "$prompt" "${model_args[@]}" \
        --permission-mode acceptEdits --allowed-tools Read Edit Grep >"$log" 2>&1
  else
    claude -p "$prompt" "${model_args[@]}" \
        --permission-mode acceptEdits --allowed-tools Read Edit Grep >"$log" 2>&1
  fi
}
export -f edit_one
printf '%s\n' "${FILES[@]}" | xargs -P "$PAR" -I{} bash -c 'edit_one "$1"' _ {}

# --- 2. VALIDATE + RECORD — serial (one sandbox; single ledger writer) ---------
# record.py is NEVER run in parallel: within one tree that is a read-modify-write
# race on the ledger (merge=union only helps across separate PRs, not in-process).
declare -a PASSED=()
for f in "${FILES[@]}"; do
  if git diff --quiet -- "$f"; then
    echo "SKIP  $f (unchanged by agent; stays in remaining)"
    continue
  fi
  vlog="$LOGDIR/$(printf '%s' "$f" | tr '/' '_').validate.log"
  if python3 .actualize/validate.py "$f" >"$vlog" 2>&1; then
    python3 .actualize/record.py "$f" done >/dev/null
    echo "PASS  $f"
    PASSED+=("$f")
  else
    echo "FAIL  $f  ($vlog)"
    if [ "${KEEP_FAILED:-0}" = "1" ]; then
      echo "      KEEP_FAILED=1 -> edit left in place (clean the tree yourself)"
    else
      git checkout -- "$f"   # revert => the file returns to remaining next pass
    fi
  fi
done

# --- 3. CHECKPOINT — commit exactly the passed .md + ledger (logs are in /tmp) -
echo ">> ${#PASSED[@]} passed"
if [ "${#PASSED[@]}" -gt 0 ] && [ "${NO_COMMIT:-0}" != "1" ]; then
  git add "${PASSED[@]}" .actualize/ledger.tsv
  git commit -q -m "actualize($ROOT): ${#PASSED[@]} file(s)"
  echo ">> committed ${#PASSED[@]} file(s) (not pushed)"
  python3 .actualize/remaining.py "$ROOT" | sed -n '2p'
elif [ "${#PASSED[@]}" -gt 0 ]; then
  echo ">> NO_COMMIT=1 -> left ${#PASSED[@]} change(s) in the tree, uncommitted"
fi
