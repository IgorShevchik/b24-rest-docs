#!/usr/bin/env bash
# Contribute actualized example sections from this fork up to the parent (upstream) repo.
# One section = one branch = one PR. This script encodes the exact, verified hand-off flow
# (see .actualize/UPSTREAM.md for the prose runbook):
#
#   1. SYNC      — fetch fresh origin/main (fork) + upstream/main (parent). Sections are
#                  always branched off FRESH upstream/main, never off fork main, because
#                  upstream keeps moving (it added content after we forked).
#   2. SELECT    — a section ships iff upstream/main STILL has legacy jsSDK calls in it AND
#                  the fork has FULLY actualized it (0 legacy, >=1 `- JS (TS)` page). This
#                  auto-skips sections upstream already modernised (no duplicates) and any
#                  half-done section. Pass section labels/paths as args to override the set;
#                  with no args the shippable set is auto-detected.
#   3. BUILD     — one branch per section off upstream/main, copying ONLY that section's
#                  api-reference/<section> content from the fork (no .actualize tooling,
#                  no .github CI, no ledger — content only, by construction).
#   4. VERIFY    — the gate that makes this trustworthy. Every built branch must pass ALL of:
#                    * every page has BOTH `- JS (TS)` and `- JS (UMD)` (countTS == countUMD > 0)
#                    * 0 legacy calls   ($b24.callMethod / callListMethod / fetchListMethod)
#                    * 0 files touched outside api-reference/<section>/
#                    * 0 tooling/CI files (.actualize/ , .github/)
#                  If ANY selected section fails, NOTHING is pushed (fail-fast) — a bad
#                  section never reaches upstream.
#   5. SHIP      — DRY by default: print the manifest + compare URLs, then remove the temp
#                  branches (tree left as found). PUSH=1 pushes the verified branches to the
#                  fork and prints the compare URLs. You then click "Create pull request" on
#                  each URL: the agent's GitHub access is restricted to the fork, so it
#                  cannot open the cross-repo PR on the parent — that one click is yours.
#
# USAGE
#   .actualize/upstream/contribute-to-upstream.sh                  # DRY: auto-detect + verify, no push
#   .actualize/upstream/contribute-to-upstream.sh crm/contacts disk   # DRY: only these sections
#   PUSH=1 .actualize/upstream/contribute-to-upstream.sh           # push the verified branches + URLs
#
# PRECONDITIONS
#   - Run from a clean clone of YOUR fork, with the actualization already on origin/main.
#   - git push rights to your fork. The script NEVER pushes to upstream.
#
# GOTCHA (cost us a false "0 TS" once): git grep patterns that start with '-' (like
#   '- JS (TS)') must be passed as  -F -e '<pattern>', and options (--cached, <rev>) must
#   come BEFORE the pattern, else git parses the leading '-' as an unknown switch.
set -uo pipefail

UPSTREAM_URL="https://github.com/bitrix-tools/b24-rest-docs.git"
FORK_OWNER="IgorShevchik"
LEGACY_RE='\$b24\.(callMethod|callListMethod|fetchListMethod)\('

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "Not a git repo — cd into your fork clone." >&2; exit 1; }

say() { printf '\033[1;34m%s\033[0m\n' "$*"; }
die() { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

[ -z "$(git status --porcelain)" ] || die "Working tree is not clean — commit or stash first."

# upstream remote present and correct
if ! git remote get-url upstream >/dev/null 2>&1; then
  say "Adding 'upstream' remote -> $UPSTREAM_URL"; git remote add upstream "$UPSTREAM_URL"
fi

say "Fetching origin/main and upstream/main ..."
git fetch -q origin main   || die "git fetch origin main failed"
git fetch -q upstream main || die "git fetch upstream main failed"

# count files in <rev> under <path> matching a fixed/ERE pattern (handles '-'-leading patterns)
count_F() { git grep -l -F -e "$1" "$2" -- "$3" 2>/dev/null | wc -l | tr -d ' '; }   # $1=pattern $2=rev $3=path
count_E() { git grep -l -E -e "$1" "$2" -- "$3" 2>/dev/null | wc -l | tr -d ' '; }

# A section qualifies for the hand-off iff upstream still has legacy calls in it AND the fork
# has fully actualized it (no legacy left, at least one TS example).
qualify() {  # $1 = label (path under api-reference/)
  local path="api-reference/$1"
  [ "$(count_E "$LEGACY_RE" upstream/main "$path")" -gt 0 ] || return 1
  [ "$(count_E "$LEGACY_RE" origin/main   "$path")" -eq 0 ] || return 1
  [ "$(count_F '- JS (TS)'  origin/main   "$path")" -gt 0 ] || return 1
}

# Shippable units mirror our PR granularity: each immediate subdir of api-reference/crm is its
# own section; every other immediate subdir of api-reference is a section.
list_candidates() {
  local d name sub
  for d in api-reference/*/; do
    name="${d#api-reference/}"; name="${name%/}"
    if [ "$name" = "crm" ]; then
      for sub in api-reference/crm/*/; do [ -d "$sub" ] && { sub="${sub%/}"; printf '%s\n' "${sub#api-reference/}"; }; done
    else
      printf '%s\n' "$name"
    fi
  done
}

# Resolve the section list: explicit args (normalised) or auto-detected.
declare -a LABELS=()
if [ "$#" -gt 0 ]; then
  for a in "$@"; do a="${a#api-reference/}"; LABELS+=("${a%/}"); done
else
  say "No sections given — auto-detecting (legacy upstream AND fully actualized in fork) ..."
  while IFS= read -r l; do qualify "$l" && LABELS+=("$l"); done < <(list_candidates)
fi
if [ "${#LABELS[@]}" -eq 0 ]; then
  say "Nothing to do — no section is both legacy upstream and fully actualized in the fork."; exit 0
fi

START="$(git rev-parse --abbrev-ref HEAD)"
declare -a BUILT=()        # slug=path for sections that built + verified clean
declare -a TEMP=()         # local temp branches to clean up on dry runs / failure
FAIL=0

cleanup() { git checkout -q "$START" 2>/dev/null || true
            for b in "${TEMP[@]:-}"; do [ -n "$b" ] && git branch -qD "$b" 2>/dev/null || true; done; }
trap 'cleanup; exit 130' INT TERM

printf '\n%-24s %5s %5s %5s %7s %7s  %s\n' "SECTION" "files" "TS" "UMD" "legacy" "scope" "result"
for label in "${LABELS[@]}"; do
  path="api-reference/$label"
  slug="actualize/${label//\//-}"
  git checkout -q -B "$slug" upstream/main || { echo "  !! cannot branch $slug"; FAIL=1; continue; }
  TEMP+=("$slug")
  git checkout -q origin/main -- "$path" 2>/dev/null
  git add -A "$path" 2>/dev/null
  if git diff --cached --quiet; then
    printf '%-24s %5s %5s %5s %7s %7s  %s\n' "$label" 0 - - - - "SKIP (already upstream)"
    git checkout -q "$START"; continue
  fi
  files=$(git diff --cached --name-only | wc -l | tr -d ' ')
  git commit -q -m "docs($label): actualize JS examples to TS + UMD (b24jssdk actions API)"
  git checkout -q "$START"

  ts=$(count_F '- JS (TS)'  "$slug" "$path")
  umd=$(count_F '- JS (UMD)' "$slug" "$path")
  legacy=$(count_E "$LEGACY_RE" "$slug" "$path")
  outside=$(git diff --name-only "upstream/main..$slug" | grep -vcE "^${path}(/|\$)" || true)
  tooling=$(git diff --name-only "upstream/main..$slug" | grep -cE '^\.actualize|^\.github' || true)

  if [ "$ts" -gt 0 ] && [ "$ts" = "$umd" ] && [ "$legacy" = 0 ] && [ "$outside" = 0 ] && [ "$tooling" = 0 ]; then
    BUILT+=("$slug=$path"); res="OK"
  else
    res="FAIL (outside=$outside tooling=$tooling)"; FAIL=1
  fi
  printf '%-24s %5s %5s %5s %7s %7s  %s\n' "$label" "$files" "$ts" "$umd" "$legacy" "$outside" "$res"
done

echo
if [ "$FAIL" -ne 0 ]; then
  cleanup
  die "One or more sections failed verification — nothing pushed. Fix the section in the fork and re-run."
fi
if [ "${#BUILT[@]}" -eq 0 ]; then cleanup; say "Nothing to ship — all selected sections are already on upstream."; exit 0; fi

print_urls() { for e in "${BUILT[@]}"; do s="${e%%=*}"
  echo "  https://github.com/bitrix-tools/b24-rest-docs/compare/main...$FORK_OWNER:$s?expand=1"; done; }

if [ "${PUSH:-0}" != "1" ]; then
  say "DRY RUN — ${#BUILT[@]} section(s) built and verified clean. Nothing pushed."
  echo "Set PUSH=1 to push these branches to the fork, then open one PR per URL (base = bitrix-tools : main):"
  print_urls
  echo
  echo "PR title:  docs(<section>): actualize JS examples to TS + UMD (b24jssdk actions API)"
  echo "PR body:   .actualize/upstream/PR-TEMPLATE.md"
  cleanup   # remove the temp branches — dry run leaves the tree as it was
  exit 0
fi

# PUSH=1 — ship the verified branches to the fork (never to upstream).
push_retry() { local b="$1" d=2 i; for i in 1 2 3 4 5; do
    git push -u origin "$b" && return 0
    echo "  push $b failed (try $i) — sleep ${d}s" >&2; sleep "$d"; d=$((d*2)); done; return 1; }

say "Pushing ${#BUILT[@]} verified branch(es) to the fork ..."
for e in "${BUILT[@]}"; do s="${e%%=*}"; push_retry "$s" || die "push failed for $s"; done
git checkout -q "$START" 2>/dev/null || true
echo
say "Done. Open one PR per section (base = bitrix-tools/b24-rest-docs : main):"
print_urls
echo
echo "Use the title/body from .actualize/upstream/PR-TEMPLATE.md for each."
