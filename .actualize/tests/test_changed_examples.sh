#!/usr/bin/env bash
# Offline tests for .actualize/ci/changed-examples.sh — the CI selection +
# sharding helper. No network. A throwaway git repo with the REAL script and a
# handful of pages exercising each selection rule.
#
# The two properties that matter:
#   selection — a page is validated iff it changed AND (has a TS tab OR is in
#               the ledger); the ledger clause is FOLLOWUPS §5, a tracked page
#               that lost its tab must reach validate.py and fail loudly there;
#   sharding  — the shards are a partition: every page appears exactly once
#               across them, so fanning out never drops or duplicates work.
#
# Run: bash .actualize/tests/test_changed_examples.sh   (exit 0 = all passed)
set -uo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the real .actualize/
FAILS=0
ok()   { echo "ok   - $1"; }
bad()  { echo "FAIL - $1"; FAILS=$((FAILS + 1)); }
check(){ if eval "$2"; then ok "$1"; else bad "$1 [cond: $2]"; fi; }

REPO="$(mktemp -d)"
trap 'rm -rf "$REPO"' EXIT

mkdir -p "$REPO/.actualize/ci" "$REPO/api-reference/tasks"
cp "$SRC/ci/changed-examples.sh" "$REPO/.actualize/ci/"
chmod +x "$REPO/.actualize/ci/changed-examples.sh"

cd "$REPO"
git init -q .
git config user.email t@t; git config user.name t

page() {  # page <path> <tab-line>
  mkdir -p "$(dirname "$1")"
  printf '# page\n\n{%% list tabs %%}\n\n%s\n\n    ```ts\n    x\n    ```\n\n{%% endlist %%}\n' "$2" > "$1"
}

# baseline commit: every page exists and is already tracked by git
page api-reference/tasks/ts.md        '- JS (TS)'
page api-reference/tasks/legacy.md    '- TS'
page api-reference/tasks/tracked.md   '- PHP CRest'     # no TS tab, but in the ledger
page api-reference/tasks/plain.md     '- PHP CRest'     # neither
page api-reference/tasks/untouched.md '- JS (TS)'
page api-reference/tasks/gone.md      '- JS (TS)'
printf 'date\tfile\tsha256\tstatus\tmethod\n' >  .actualize/ledger.tsv
printf 'd\tapi-reference/tasks/tracked.md\ts\tdone\tm\n' >> .actualize/ledger.tsv
git add -A; git commit -qm base
BASE="$(git rev-parse HEAD)"

# the change under test
for f in ts legacy tracked plain; do echo "edit" >> "api-reference/tasks/$f.md"; done
git rm -q api-reference/tasks/gone.md
git add -A; git commit -qm change

list() { bash .actualize/ci/changed-examples.sh "$@"; }
out="$(list "$BASE")"
has(){ printf '%s\n' "$out" | grep -qxF "api-reference/tasks/$1.md"; }

# 1) selection rules
check "TS tab (canonical) selected"            'has ts'
check "TS tab (legacy spelling) selected"      'has legacy'
check "ledger-tracked, tab-less selected (§5)" 'has tracked'
check "untracked + tab-less NOT selected"      '! has plain'
check "unchanged page NOT selected"            '! has untouched'
check "deleted page NOT selected"              '! has gone'
check "exactly 3 pages selected"               '[ "$(printf "%s\n" "$out" | grep -c .)" -eq 3 ]'

# 2) unreachable base -> fall back to the root commit rather than selecting nothing
out_bad="$(list 0000000000000000000000000000000000000000 2>/dev/null)"
check "unreachable base falls back to root"    '[ "$(printf "%s\n" "$out_bad" | grep -c .)" -ge 3 ]'
check "empty base falls back to root"          '[ "$(list "" 2>/dev/null | grep -c .)" -ge 3 ]'

# 3) sharding is a partition of the list, for every shard count
printf '%s\n' "$out" > full.txt
for n in 1 2 3 5; do
  : > union.txt
  for i in $(seq 0 $((n - 1))); do
    bash .actualize/ci/changed-examples.sh --shard "$i/$n" full.txt >> union.txt
  done
  check "shards n=$n cover the list exactly once" \
        '[ "$(sort union.txt | md5sum)" = "$(sort full.txt | md5sum)" ] && [ "$(wc -l < union.txt)" -eq "$(wc -l < full.txt)" ]'
done
check "shards stay balanced (n=2, 3 pages -> 2/1)" \
      '[ "$(bash .actualize/ci/changed-examples.sh --shard 0/2 full.txt | wc -l)" -eq 2 ]'

# 4) usage errors are refused, not silently treated as "nothing to do"
shard_rc(){ bash .actualize/ci/changed-examples.sh --shard "$1" "${2:-full.txt}" >/dev/null 2>&1; echo $?; }
check "index == count rejected"      '[ "$(shard_rc 2/2)" -eq 64 ]'
check "count == 0 rejected"          '[ "$(shard_rc 0/0)" -eq 64 ]'
check "non-numeric shard rejected"   '[ "$(shard_rc a/2)" -eq 64 ]'
check "missing list file rejected"   '[ "$(shard_rc 0/2 nope.txt)" -eq 66 ]'

echo
if [ "$FAILS" -eq 0 ]; then echo "ALL changed-examples TESTS PASSED"; exit 0
else echo "$FAILS changed-examples TEST(S) FAILED"; exit 1; fi
