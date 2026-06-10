#!/usr/bin/env bash
# Offline tests for .actualize/upstream/contribute-to-upstream.sh — the upstream hand-off.
# No network, no GitHub: two local bare repos stand in for the remotes (origin = the fork,
# upstream = the parent), plus a working clone. Markdown "examples" are just files carrying
# the markers the script greps for (`- JS`, `- JS (TS)`, `- JS (UMD)`, `$b24.callMethod(`).
#
# Scenarios:
#   1. AUTO-DETECT (dry): selects only sections that are legacy upstream AND fully actualized
#      in the fork; excludes a half-done section and a section upstream already modernised;
#      verifies, prints URLs, pushes nothing, leaves the tree clean.
#   2. VERIFY GATE: an explicitly-named section whose pages are not all TS+UMD (one page has
#      TS but no UMD) FAILS the gate -> non-zero exit, nothing pushed.
#   3. PUSH=1: a clean section is actually pushed to the fork remote.
#   4. ALREADY UPSTREAM: a section identical to upstream produces no diff -> "nothing to ship",
#      exit 0, nothing pushed.
#
# Run: bash .actualize/tests/test_contribute_upstream.sh   (exit 0 = all passed)
set -uo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the real .actualize/
SCRIPT="$SRC_DIR/upstream/contribute-to-upstream.sh"
FAILS=0
ok()    { echo "ok   - $1"; }
bad()   { echo "FAIL - $1"; FAILS=$((FAILS + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1 [cond: $2]"; fi; }

UP="" OR="" WORK=""

mk_legacy() { mkdir -p "$WORK/$(dirname "$1")"; printf '# t\n\n- JS\n```js\n$b24.callMethod("x", {});\n```\n' > "$WORK/$1"; }
mk_full()   { mkdir -p "$WORK/$(dirname "$1")"; printf '# t\n\n- JS (TS)\n```ts\n$b24.actions.v2.call.make({});\n```\n\n- JS (UMD)\n```js\nB24Js.hello();\n```\n' > "$WORK/$1"; }
mk_tsonly() { mkdir -p "$WORK/$(dirname "$1")"; printf '# t\n\n- JS (TS)\n```ts\n$b24.actions.v2.call.make({});\n```\n' > "$WORK/$1"; }

new_world() {   # fresh origin(fork)+upstream(parent) bare remotes + a working clone with the real script
  UP="$(mktemp -d)/up.git"; OR="$(mktemp -d)/or.git"; WORK="$(mktemp -d)/work"
  git init -q --bare "$UP"; git init -q --bare "$OR"
  git clone -q "$OR" "$WORK" 2>/dev/null
  git -C "$WORK" config user.email t@t.t; git -C "$WORK" config user.name t
  git -C "$WORK" config commit.gpgsign false; git -C "$WORK" config tag.gpgsign false
  git -C "$WORK" remote add upstream "$UP"
  git -C "$WORK" checkout -q -b main
  mkdir -p "$WORK/.actualize/upstream"
  cp "$SCRIPT" "$WORK/.actualize/upstream/"; chmod +x "$WORK/.actualize/upstream/contribute-to-upstream.sh"
}
commit_upstream() { git -C "$WORK" add -A; git -C "$WORK" commit -q -m upstream; git -C "$WORK" push -q upstream HEAD:main; }
commit_fork()     { git -C "$WORK" add -A; git -C "$WORK" commit -q -m fork;     git -C "$WORK" push -q origin   HEAD:main; }
run()  { ( cd "$WORK" && "$@" bash .actualize/upstream/contribute-to-upstream.sh "${ARGS[@]}" ) 2>&1; }
remote_has() { [ -n "$(git -C "$WORK" ls-remote origin "refs/heads/$1" 2>/dev/null)" ]; }
clean_world() { rm -rf "$(dirname "$UP")" "$(dirname "$OR")" "$(dirname "$WORK")"; }

# ============================ 1) AUTO-DETECT (dry) =============================
new_world
# upstream: ship1/ship2/halfdone are legacy; "already" is modernised upstream
mk_legacy api-reference/ship1/a.md; mk_legacy api-reference/ship2/a.md
mk_legacy api-reference/halfdone/a.md
mk_full   api-reference/already/a.md
commit_upstream
# fork: ship1/ship2 actualized; halfdone still legacy; already unchanged
mk_full api-reference/ship1/a.md; mk_full api-reference/ship2/a.md
commit_fork
ARGS=(); out="$(run)"; rc=$?
check "auto: exit 0"                  "[ $rc -eq 0 ]"
check "auto: ship1 selected OK"       "printf '%s' \"\$out\" | grep -E 'ship1' | grep -q 'OK'"
check "auto: ship2 selected OK"       "printf '%s' \"\$out\" | grep -E 'ship2' | grep -q 'OK'"
check "auto: halfdone excluded"       "! printf '%s' \"\$out\" | grep -qE '^halfdone'"
check "auto: already excluded"        "! printf '%s' \"\$out\" | grep -qE '^already'"
check "auto: announces DRY RUN"       "printf '%s' \"\$out\" | grep -q 'DRY RUN'"
check "auto: prints a compare URL"    "printf '%s' \"\$out\" | grep -q 'compare/main...IgorShevchik:actualize/ship1'"
check "auto: pushed nothing"          "! remote_has 'actualize/ship1'"
check "auto: tree left clean"         "[ -z \"\$(git -C \"\$WORK\" status --porcelain)\" ]"
clean_world

# ============================ 2) VERIFY GATE rejects ==========================
new_world
mk_legacy api-reference/badumd/a.md; mk_legacy api-reference/badumd/b.md
commit_upstream
mk_full api-reference/badumd/a.md; mk_tsonly api-reference/badumd/b.md   # page b: TS but no UMD
commit_fork
ARGS=(badumd); out="$(run)"; rc=$?
check "gate: non-zero exit"           "[ $rc -ne 0 ]"
check "gate: reports FAIL"            "printf '%s' \"\$out\" | grep -q 'FAIL'"
check "gate: says nothing pushed"     "printf '%s' \"\$out\" | grep -qi 'nothing pushed'"
check "gate: pushed nothing"          "! remote_has 'actualize/badumd'"
check "gate: tree left clean"         "[ -z \"\$(git -C \"\$WORK\" status --porcelain)\" ]"
clean_world

# ============================ 3) PUSH=1 ships =================================
new_world
mk_legacy api-reference/ship1/a.md; commit_upstream
mk_full   api-reference/ship1/a.md; commit_fork
ARGS=(ship1); out="$( PUSH=1 run )"; rc=$?
check "push: exit 0"                  "[ $rc -eq 0 ]"
check "push: announces Done"          "printf '%s' \"\$out\" | grep -q 'Done'"
check "push: branch on fork remote"   "remote_has 'actualize/ship1'"
clean_world

# ============================ 4) ALREADY UPSTREAM ============================
new_world
mk_full api-reference/already/a.md; commit_upstream
# fork identical to upstream (no actualization diff): point origin/main at the same commit
git -C "$WORK" push -q origin HEAD:main
ARGS=(already); out="$(run)"; rc=$?
check "already: exit 0"               "[ $rc -eq 0 ]"
check "already: nothing to ship"      "printf '%s' \"\$out\" | grep -qi 'nothing to ship'"
check "already: pushed nothing"       "! remote_has 'actualize/already'"
clean_world

echo
if [ "$FAILS" -eq 0 ]; then echo "ALL contribute-to-upstream TESTS PASSED"; exit 0
else echo "$FAILS contribute-to-upstream TEST(S) FAILED"; exit 1; fi
