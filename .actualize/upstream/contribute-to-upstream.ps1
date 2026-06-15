<#
  Windows mirror of .actualize/upstream/contribute-to-upstream.sh — the upstream hand-off.
  The bash script is the canonical, CI-tested entry point (see .actualize/UPSTREAM.md and
  .actualize/tests/test_contribute_upstream.sh); this is a faithful PowerShell port for a
  maintainer working on Windows without Git-Bash/WSL.

  WHAT IT DOES (same as the .sh)
    1. SYNC   - fetch fresh origin/main (fork) + upstream/main (parent).
    2. SELECT - a section ships iff upstream/main still has legacy jsSDK calls AND the fork has
                fully actualized it (0 legacy, >=1 "- JS (TS)" page). Pass section labels/paths
                as args to override; with none, the set is auto-detected. crm/* subdirs are
                their own sections; every other api-reference/<dir> is one section.
    3. BUILD  - one branch actualize/<slug> per section off upstream/main, copying ONLY that
                section's api-reference/<section> content from the fork (no tooling, no CI).
    4. VERIFY - each branch must have every page carry BOTH "- JS (TS)" and "- JS (UMD)"
                (countTS == countUMD > 0), 0 legacy calls, 0 files outside the section, 0
                tooling/CI files. Any failure aborts the run and pushes nothing.
    5. SHIP   - DRY by default (print manifest + compare URLs, remove temp branches). Set the
                environment variable PUSH=1 to push the verified branches to the fork. The
                script never pushes to upstream; you click "Create pull request" on each URL.

  USAGE  (PowerShell)
    powershell -ExecutionPolicy Bypass -File .actualize\upstream\contribute-to-upstream.ps1
    powershell -ExecutionPolicy Bypass -File .actualize\upstream\contribute-to-upstream.ps1 crm/contacts disk
    $env:PUSH=1; powershell -ExecutionPolicy Bypass -File .actualize\upstream\contribute-to-upstream.ps1
#>
param([Parameter(ValueFromRemainingArguments = $true)] [string[]] $SectionArgs)
$ErrorActionPreference = "Stop"

$UpstreamUrl = "https://github.com/bitrix-tools/b24-rest-docs.git"
$ForkOwner   = "IgorShevchik"
$LegacyRe    = '\$b24\.(callMethod|callListMethod|fetchListMethod)\('

function Say ($m) { Write-Host $m -ForegroundColor Cyan }
function Die ($m) { Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }

# count files in <rev> under <path> matching a fixed (F) or ERE (E) pattern; handles '-'-leading patterns via -e
function Count-Match { param($Mode, $Pattern, $Rev, $Path)
  $flag = if ($Mode -eq 'F') { '-F' } else { '-E' }
  $out = & git grep -l $flag -e $Pattern $Rev -- $Path 2>$null
  if (-not $out) { return 0 }
  return @($out).Count
}
function Qualify { param($Label)
  $path = "api-reference/$Label"
  if ((Count-Match 'E' $LegacyRe 'upstream/main' $path) -le 0) { return $false }
  if ((Count-Match 'E' $LegacyRe 'origin/main'   $path) -ne 0) { return $false }
  if ((Count-Match 'F' '- JS (TS)' 'origin/main' $path) -le 0) { return $false }
  return $true
}

$root = (& git rev-parse --show-toplevel) 2>$null
if (-not $root) { Die "Not a git repo - cd into your fork clone." }
Set-Location $root
if (& git status --porcelain) { Die "Working tree is not clean - commit or stash first." }

& git remote get-url upstream *> $null
if ($LASTEXITCODE -ne 0) { Say "Adding 'upstream' remote -> $UpstreamUrl"; & git remote add upstream $UpstreamUrl }

Say "Fetching origin/main and upstream/main ..."
& git fetch -q origin main;   if ($LASTEXITCODE -ne 0) { Die "git fetch origin main failed" }
& git fetch -q upstream main; if ($LASTEXITCODE -ne 0) { Die "git fetch upstream main failed" }

# Resolve the section list: explicit args (normalised) or auto-detected.
if ($SectionArgs) {
  $labels = $SectionArgs | ForEach-Object { (($_ -replace '^api-reference/', '') -replace '/$', '') }
} else {
  Say "No sections given - auto-detecting (legacy upstream AND fully actualized in fork) ..."
  $cands = @()
  Get-ChildItem -Path api-reference -Directory | ForEach-Object {
    if ($_.Name -eq 'crm') { Get-ChildItem -Path $_.FullName -Directory | ForEach-Object { $cands += "crm/$($_.Name)" } }
    else { $cands += $_.Name }
  }
  $labels = $cands | Where-Object { Qualify $_ }
}
if (-not $labels -or @($labels).Count -eq 0) {
  Say "Nothing to do - no section is both legacy upstream and fully actualized in the fork."; exit 0
}

$start = (& git rev-parse --abbrev-ref HEAD).Trim()
$built = @()   # slugs verified clean
$temp  = @()   # temp branches to clean up
$fail  = $false

function Cleanup {
  & git checkout -q $start *> $null
  foreach ($b in $temp) { if ($b) { & git branch -qD $b *> $null } }
}

Write-Host ("`n{0,-24} {1,5} {2,5} {3,5} {4,7} {5,7}  {6}" -f "SECTION","files","TS","UMD","legacy","scope","result")
foreach ($label in $labels) {
  $path = "api-reference/$label"
  $slug = "actualize/" + ($label -replace '/', '-')
  & git checkout -q -B $slug upstream/main; if ($LASTEXITCODE -ne 0) { Write-Host "  !! cannot branch $slug"; $fail = $true; continue }
  $temp += $slug
  & git checkout -q origin/main -- $path 2>$null
  & git add -A $path 2>$null
  & git diff --cached --quiet
  if ($LASTEXITCODE -eq 0) {
    Write-Host ("{0,-24} {1,5} {2,5} {3,5} {4,7} {5,7}  {6}" -f $label,0,"-","-","-","-","SKIP (already upstream)")
    & git checkout -q $start; continue
  }
  $files = @(& git diff --cached --name-only).Count
  & git commit -q -m "docs($label): actualize JS examples to TS + UMD"
  & git checkout -q $start

  $ts      = Count-Match 'F' '- JS (TS)'  $slug $path
  $umd     = Count-Match 'F' '- JS (UMD)' $slug $path
  $legacy  = Count-Match 'E' $LegacyRe    $slug $path
  $diff    = & git diff --name-only "upstream/main..$slug"
  $esc     = [regex]::Escape($path)
  $outside = @($diff | Where-Object { $_ -notmatch "^$esc(/|$)" }).Count
  $tooling = @($diff | Where-Object { $_ -match '^\.actualize|^\.github' }).Count

  if ($ts -gt 0 -and $ts -eq $umd -and $legacy -eq 0 -and $outside -eq 0 -and $tooling -eq 0) {
    $built += $slug; $res = "OK"
  } else { $res = "FAIL (outside=$outside tooling=$tooling)"; $fail = $true }
  Write-Host ("{0,-24} {1,5} {2,5} {3,5} {4,7} {5,7}  {6}" -f $label,$files,$ts,$umd,$legacy,$outside,$res)
}

Write-Host ""
if ($fail) { Cleanup; Die "One or more sections failed verification - nothing pushed. Fix the section in the fork and re-run." }
if (@($built).Count -eq 0) { Cleanup; Say "Nothing to ship - all selected sections are already on upstream."; exit 0 }

function Print-Urls { foreach ($s in $built) { Write-Host "  https://github.com/bitrix-tools/b24-rest-docs/compare/main...${ForkOwner}:${s}?expand=1" } }

if ($env:PUSH -ne "1") {
  Say ("DRY RUN - {0} section(s) built and verified clean. Nothing pushed." -f @($built).Count)
  Write-Host "Set `$env:PUSH=1 to push these branches to the fork, then open one PR per URL (base = bitrix-tools : main):"
  Print-Urls
  Write-Host ""
  Write-Host "PR title:  docs(<section>): actualize JS examples to TS + UMD"
  Write-Host "PR body:   .actualize/upstream/PR-TEMPLATE.md"
  Cleanup
  exit 0
}

Say ("Pushing {0} verified branch(es) to the fork ..." -f @($built).Count)
foreach ($s in $built) {
  $ok = $false
  foreach ($d in 2,4,8,16,0) {
    & git push -u origin $s; if ($LASTEXITCODE -eq 0) { $ok = $true; break }
    if ($d -gt 0) { Write-Host "  push $s failed - retry in ${d}s"; Start-Sleep -Seconds $d }
  }
  if (-not $ok) { Die "push failed for $s" }
}
& git checkout -q $start *> $null
Write-Host ""
Say "Done. Open one PR per section (base = bitrix-tools/b24-rest-docs : main):"
Print-Urls
Write-Host ""
Write-Host "Use the title/body from .actualize/upstream/PR-TEMPLATE.md for each."
