#!/usr/bin/env bash
# Which example pages does a CI run have to validate — and, on a large change
# set, which slice of them does this runner take.
#
# A page qualifies when it changed between <base> and HEAD under api-reference/
# AND (it carries an actualized TS tab OR it is tracked in the ledger). The
# ledger clause is deliberate (FOLLOWUPS §5): a tracked page that LOSES its tab
# must fail loudly in validate.py's structural check rather than be skipped.
#
# Sharding exists because the list is unbounded. A routine PR touches a handful
# of pages; an upstream resync touches ~1500, which walks straight into the job
# timeout when one runner validates them serially. Round-robin slicing lets the
# workflow fan the same list across N runners — every page still runs, nothing
# is capped or dropped.
#
# Usage:
#   changed-examples.sh <base-ref>            list every qualifying page
#   changed-examples.sh --shard I/N <file>    print shard I of N of an existing list
#
# Exit: 0 on success (an empty list is success), 64 on usage error, 66 on a
# missing list file.
set -euo pipefail

usage() {
  sed -n '/^# Usage:/,/^# Exit:/p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2
  exit 64
}

# --- shard mode: slice a list this script produced earlier --------------------
if [ "${1:-}" = "--shard" ]; then
  [ "$#" -eq 3 ] || usage
  spec="$2"; list="$3"
  index="${spec%%/*}"; count="${spec##*/}"
  case "${index}:${count}" in
    *[!0-9:]*|:*|*:) usage ;;
  esac
  [ "$count" -gt 0 ] && [ "$index" -lt "$count" ] || usage
  [ -f "$list" ] || { echo "changed-examples.sh: no such list: $list" >&2; exit 66; }
  # (NR-1) % count == index — every line lands in exactly one shard, and the
  # shards stay within one line of each other in size.
  awk -v i="$index" -v n="$count" '(NR - 1) % n == i' "$list"
  exit 0
fi

# --- list mode ----------------------------------------------------------------
[ "$#" -eq 1 ] || usage
base="$1"
cd "$(git rev-parse --show-toplevel)"

# A missing or unreachable base (new branch, first push, force-push) means we
# cannot tell what changed, so fall back to the root commit and validate the
# whole corpus rather than silently validating nothing.
if [ -z "$base" ] || ! git cat-file -e "${base}^{commit}" 2>/dev/null; then
  base="$(git rev-list --max-parents=0 HEAD | tail -1)"
  echo "changed-examples.sh: base unavailable, falling back to root commit ${base}" >&2
fi

# Read the ledger into a variable, not a file in the checkout, so the scan below
# cannot pick up its own scratch file.
ledger_paths=""
[ -f .actualize/ledger.tsv ] && ledger_paths="$(cut -f2 .actualize/ledger.tsv)"

git diff --name-only "$base" HEAD -- 'api-reference/**/*.md' | while IFS= read -r f; do
  [ -n "$f" ] || continue
  [ -f "$f" ] || continue          # deleted or renamed away — nothing to validate
  if grep -qE '^- (JS \(TS\)|TS)$' "$f" || grep -qxF "$f" <<<"$ledger_paths"; then
    printf '%s\n' "$f"
  fi
done
