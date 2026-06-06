#!/usr/bin/env bash
#
# Contribute the actualized CRM examples from this fork up to the parent repo.
# One section = one branch = one PR (per .actualize/UPSTREAM.md).
#
# WHAT IT DOES
#   For each section it:
#     1. creates a branch off the FRESH upstream/main  (actualize/crm-<section>)
#     2. copies in ONLY that section's content from your fork's main
#        (api-reference/crm/<section>/ — no .actualize tooling, no ledger)
#     3. commits with the conventional message
#     4. pushes the branch to your fork (origin)
#     5. prints the URL to open the upstream PR (base: bitrix-tools : main)
#
# PRECONDITIONS
#   - Run from a CLEAN clone of YOUR fork (github.com/IgorShevchik/b24-rest-docs),
#     with your fork already synced to upstream (you just did the sync).
#   - git push rights to your fork. The script never pushes to upstream.
#
# USAGE
#   bash .actualize/upstream/contribute-to-upstream.sh
#
set -euo pipefail

UPSTREAM_URL="https://github.com/bitrix-tools/b24-rest-docs.git"
FORK_OWNER="IgorShevchik"
# Sections to ship (reviewed). Add "currency" if you also want to contribute it.
SECTIONS=(status deals leads companies)

say() { printf '\033[1;34m%s\033[0m\n' "$*"; }
die() { printf '\033[1;31mERROR: %s\033[0m\n' "$*" >&2; exit 1; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "Not a git repo — cd into your fork clone."
[ -z "$(git status --porcelain)" ] || die "Working tree is not clean — commit or stash first."

# Ensure the upstream remote exists and points at the parent.
if ! git remote get-url upstream >/dev/null 2>&1; then
  say "Adding 'upstream' remote -> $UPSTREAM_URL"
  git remote add upstream "$UPSTREAM_URL"
fi

say "Fetching origin/main and upstream/main ..."
git fetch origin main
git fetch upstream main

# Sanity: the fork must already carry the actualization.
if git grep -qE '\$b24\.(callMethod|callListMethod|fetchListMethod)' origin/main -- api-reference/crm/status 2>/dev/null; then
  die "origin/main still has legacy jsSDK calls in crm/status — is your fork synced/actualized?"
fi

start_branch="$(git rev-parse --abbrev-ref HEAD)"
declare -a PR_LINKS=()

for s in "${SECTIONS[@]}"; do
  branch="actualize/crm-$s"
  say "=== crm/$s -> $branch ==="
  git checkout -B "$branch" upstream/main
  # Bring in ONLY this section's actualized content from the fork main.
  git checkout origin/main -- "api-reference/crm/$s"
  git add "api-reference/crm/$s"
  if git diff --cached --quiet; then
    echo "  no diff vs upstream for crm/$s — skipping (already actualized upstream?)"
    git checkout -q "$start_branch"; continue
  fi
  files=$(git diff --cached --name-only | wc -l | tr -d ' ')
  git commit -q -m "docs(crm/$s): actualize JS examples to TS + UMD (b24jssdk actions API)"
  echo "  committed $files file(s); pushing ..."
  git push -u origin "$branch"
  PR_LINKS+=("https://github.com/bitrix-tools/b24-rest-docs/compare/main...$FORK_OWNER:$branch?expand=1")
done

git checkout -q "$start_branch" 2>/dev/null || true

echo
say "Done. Open one PR per section (base = bitrix-tools/b24-rest-docs : main):"
for l in "${PR_LINKS[@]}"; do echo "  $l"; done
echo
echo "Use the title/body from .actualize/upstream/PR-TEMPLATE.md for each."
