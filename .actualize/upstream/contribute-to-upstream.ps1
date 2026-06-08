<#
  Contribute the actualized example sections from this fork up to the parent repo.
  One section = one branch = one PR (per .actualize/UPSTREAM.md).

  WHAT IT DOES
    For each section it:
      1. creates a branch off the FRESH upstream/main  (actualize/<slug>)
      2. copies in ONLY that section's content from your fork's main
         (no .actualize tooling, no ledger, no CI files)
      3. commits with the conventional message  docs(<label>): ...
      4. pushes the branch to your fork (origin)
      5. prints the URL to open the upstream PR (base: bitrix-tools : main)

  PRECONDITIONS
    - Run from a CLEAN clone of YOUR fork (github.com/IgorShevchik/b24-rest-docs),
      synced to upstream (origin/main already carries the actualization).
    - git push rights to your fork. The script never pushes to upstream.

  USAGE  (PowerShell)
    powershell -ExecutionPolicy Bypass -File .actualize\upstream\contribute-to-upstream.ps1
#>

$ErrorActionPreference = "Stop"

$UpstreamUrl = "https://github.com/bitrix-tools/b24-rest-docs.git"
$ForkOwner   = "IgorShevchik"

# Sections to ship: Label -> branch actualize/<Label with '/'->'-'> and commit "docs(<Label>): ..."
# Path -> the content copied from origin/main.
$Sections = @(
  @{ Label = "crm/status";    Path = "api-reference/crm/status" },
  @{ Label = "crm/deals";     Path = "api-reference/crm/deals" },
  @{ Label = "crm/leads";     Path = "api-reference/crm/leads" },
  @{ Label = "crm/companies"; Path = "api-reference/crm/companies" },
  @{ Label = "crm/contacts";  Path = "api-reference/crm/contacts" },
  @{ Label = "crm/currency";  Path = "api-reference/crm/currency" },
  @{ Label = "calendar";      Path = "api-reference/calendar" }
)

function Say ($m) { Write-Host $m -ForegroundColor Cyan }
function Die ($m) { Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
function Git { & git @args; if ($LASTEXITCODE -ne 0) { Die ("git " + ($args -join " ") + " failed") } }

# --- preflight ---
& git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE -ne 0) { Die "Not a git repo - cd into your fork clone." }
if (& git status --porcelain) { Die "Working tree is not clean - commit or stash first." }

& git remote get-url upstream *> $null
if ($LASTEXITCODE -ne 0) { Say "Adding 'upstream' remote -> $UpstreamUrl"; Git remote add upstream $UpstreamUrl }

Say "Fetching origin/main and upstream/main ..."
Git fetch origin main
Git fetch upstream main

# Sanity: the fork must already carry the actualization.
& git grep -qE '\$b24\.(callMethod|callListMethod|fetchListMethod)' origin/main -- api-reference/crm/status 2> $null
if ($LASTEXITCODE -eq 0) { Die "origin/main still has legacy jsSDK calls in crm/status - is your fork synced/actualized?" }

$startBranch = (& git rev-parse --abbrev-ref HEAD).Trim()
$prLinks = @()

foreach ($s in $Sections) {
  $label = $s.Label
  $path  = $s.Path
  $slug  = "actualize/" + ($label -replace '/', '-')
  Say "=== $label ($path) -> $slug ==="
  Git checkout -B $slug upstream/main
  # Bring in ONLY this section's actualized content from the fork main.
  Git checkout origin/main -- $path
  Git add $path
  & git diff --cached --quiet
  if ($LASTEXITCODE -eq 0) {
    Write-Host "  no diff vs upstream for $label - skipping"
    Git checkout -q $startBranch; continue
  }
  $files = (& git diff --cached --name-only | Measure-Object -Line).Lines
  Git commit -q -m "docs($label): actualize JS examples to TS + UMD (b24jssdk actions API)"
  Write-Host "  committed $files file(s); pushing ..."
  Git push -u origin $slug
  $prLinks += "https://github.com/bitrix-tools/b24-rest-docs/compare/main...${ForkOwner}:${slug}?expand=1"
}

& git checkout -q $startBranch *> $null

Write-Host ""
Say "Done. Open one PR per section (base = bitrix-tools/b24-rest-docs : main):"
$prLinks | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Use the title/body from .actualize/upstream/PR-TEMPLATE.md for each."
