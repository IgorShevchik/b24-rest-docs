#!/usr/bin/env bash
# .actualize/run-section.sh — drain a whole ROOT to zero remaining, with auto-retry.
#
# A thin layer OVER run-batch.sh (it does not modify or bypass it — every edit still
# goes through run-batch's clean-tree / blast-radius / secret-scan guards). It just
# automates the "parallel for speed, then sequential to finish" pattern we hit on
# every real section:
#
#   PARALLEL drain  — RUN=1 run-batch ROOT N PAR, repeated while it makes progress.
#     Fast bulk edits. ~3% of files miss under PAR>1 (a transient where the nested
#     agent didn't apply the edit) or are large list-methods that choke in parallel;
#     run-batch reverts those, so they stay in "remaining".
#   SEQUENTIAL mop-up — RUN=1 run-batch ROOT 0 1, repeated while it makes progress.
#     Every still-remaining file, one at a time (full resource + timeout each). This
#     drains the transient/large-list stragglers that a parallel pass keeps missing.
#
# Each phase stops on a PLATEAU (remaining count unchanged across a pass) so it can
# never spin on a genuinely stuck file (a deterministic validate FAIL): the parallel
# phase hands such files to the sequential phase, and if they fail even sequentially
# the run ends with them still listed — reported, not looped.
#
# Usage:
#   .actualize/run-section.sh ROOT [N] [PAR]         # DRY RUN (delegates to run-batch)
#   RUN=1 .actualize/run-section.sh ROOT [N] [PAR]   # actually run
#     ROOT  walk directory             (default: api-reference/tasks)
#     N     files per parallel batch    (default: 40) — checkpoint granularity
#     PAR   parallel agent edits        (default: 3)  — sequential mop-up is always 1
#
# Env: passes RUN / EDIT_TIMEOUT / CLAUDE_MODEL / CLAUDE_BIN / NO_COMMIT through to
#   run-batch unchanged. MAX_PASSES caps each phase (default 50) as a belt-and-braces
#   stop in case a remaining-count probe ever misbehaves.
#
# Exit: 0 = ROOT fully drained (0 remaining); 1 = run-batch hard-aborted (dirty tree,
#   SECURITY ABORT, bad args, commit failure) — surfaced verbatim; 2 = drained as far
#   as possible but some files remain stuck (fail/skip even sequentially); 130 = interrupted.
set -uo pipefail

cd "$(dirname "$0")/.." || { echo "cannot cd to repo root" >&2; exit 1; }
[ -f .actualize/remaining.py ] || { echo "run from the b24-rest-docs repo" >&2; exit 1; }
RUNBATCH=".actualize/run-batch.sh"
[ -x "$RUNBATCH" ] || { echo "run-batch.sh not found/executable at $RUNBATCH" >&2; exit 1; }

ROOT="${1:-api-reference/tasks}"
N="${2:-40}"
PAR="${3:-3}"
MAX_PASSES="${MAX_PASSES:-50}"

# --- DRY RUN: just delegate to run-batch's own dry-run plan and stop -----------
if [ "${RUN:-0}" != "1" ]; then
  echo ">> run-section DRY RUN — showing run-batch plan for the first parallel batch."
  echo "   set RUN=1 to drain '$ROOT' (parallel PAR=$PAR, then sequential PAR=1)."
  "$RUNBATCH" "$ROOT" "$N" "$PAR"
  exit $?
fi

# remaining count for ROOT, or empty string on probe failure (treated as fatal below).
remaining_count() {
  python3 .actualize/remaining.py "$ROOT" 2>/dev/null \
    | grep -oE 'not done\): [0-9]+' | grep -oE '[0-9]+$'
}

# Drain one phase: repeatedly invoke run-batch with the given (N, PAR) until ROOT is
# empty, the count plateaus (no progress => stragglers for the next phase), or
# run-batch hard-aborts. Echoes nothing of its own beyond a per-pass header; the real
# per-file PASS/FAIL/SKIP lines come from run-batch. Returns:
#   0 drained to zero | 10 plateau (progress stalled) | else = run-batch's abort code.
drain_phase() {
  local pass_n="$1" pass_par="$2" label="$3"
  local prev=-1 rem rc i=0
  while :; do
    rem="$(remaining_count)"
    if [ -z "$rem" ]; then
      echo ">> remaining.py probe failed for ROOT='$ROOT' — aborting." >&2
      return 1
    fi
    [ "$rem" -eq 0 ] && return 0
    if [ "$rem" -eq "$prev" ]; then
      return 10   # count didn't move after a full pass => this phase can't progress
    fi
    i=$((i + 1))
    if [ "$i" -gt "$MAX_PASSES" ]; then
      echo ">> $label: hit MAX_PASSES=$MAX_PASSES with $rem remaining — stopping phase." >&2
      return 10
    fi
    prev="$rem"
    echo ">> $label pass $i: $rem remaining (N=$pass_n PAR=$pass_par)"
    RUN=1 "$RUNBATCH" "$ROOT" "$pass_n" "$pass_par"
    rc=$?
    # run-batch: 0 ok | 3 no-progress(0 passed) — both fine to loop on (plateau guard
    # above stops us). 1 abort / 2 bad args / 130 interrupt => propagate immediately.
    case "$rc" in
      0|3) : ;;
      *)   return "$rc" ;;
    esac
  done
}

echo "############ run-section: draining $ROOT ############"

# --- Phase 1: PARALLEL --------------------------------------------------------
drain_phase "$N" "$PAR" "PARALLEL"; rc=$?
case "$rc" in
  0)  echo ">> $ROOT fully drained in the parallel phase."; exit 0 ;;
  10) : ;;                                  # plateau => fall through to sequential mop-up
  *)  echo ">> run-batch aborted (code $rc) during parallel phase — stopping." >&2; exit "$rc" ;;
esac

# --- Phase 2: SEQUENTIAL mop-up (PAR=1, all remaining each pass) ---------------
echo ">> parallel phase plateaued — sequential mop-up of stragglers (PAR=1)."
drain_phase 0 1 "SEQUENTIAL"; rc=$?
case "$rc" in
  0)  echo ">> $ROOT fully drained after sequential mop-up."; exit 0 ;;
  10) stuck="$(remaining_count)"
      echo ">> STUCK: $stuck file(s) under $ROOT fail or are skipped even sequentially." >&2
      echo "   Inspect them by hand (re-run with KEEP_FAILED=1 to keep the agent logs)." >&2
      exit 2 ;;
  *)  echo ">> run-batch aborted (code $rc) during sequential phase — stopping." >&2; exit "$rc" ;;
esac
