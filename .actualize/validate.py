#!/usr/bin/env python3
"""Validate the b24jssdk TS + UMD examples inside a documentation .md file.

Checks (cheapest first):
  1. structural: legacy "- JS" tab is gone, "- TS" and "- UMD" tabs are present;
  2. extraction: take the single ```ts block and the single UMD <script> from
     INSIDE the first {% list tabs %} … {% endlist %} region (not anywhere else);
  3. forbidden tokens: no callMethod / callListMethod / fetchListMethod /
     processResult / processData; an actions.v{2,3} call is present in BOTH tabs;
  4. types: `tsc --strict` against a reproducible, lockfile-pinned toolchain
     (.actualize/typecheck/package*.json installed with `npm ci --ignore-scripts`);
  5. syntax: `node --check` on the UMD inline script.

Usage:
  python3 .actualize/validate.py <path-to-md> [--project DIR]

--project is a trusted local argument (the sandbox dir, default .actualize/.tscheck);
in CI it is never overridden. Exit code 0 = PASS, non-zero = FAIL. Toolchain
versions are pinned by .actualize/typecheck/package-lock.json (bump deliberately —
see README).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap

import _tabs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ENV_DIR = os.path.join(HERE, "typecheck")  # committed package.json + package-lock.json

NPM_TIMEOUT = 600
TSC_TIMEOUT = 300
NODE_TIMEOUT = 120

FORBIDDEN = ["callMethod", "callListMethod", "fetchListMethod",
             "processResult", "processData"]


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def extract(md_path):
    """Return (ts_code, umd_inner_js) extracted from inside the tabs region."""
    with open(md_path, encoding="utf-8") as f:
        s = f.read()

    if "- JS\n" in s:
        fail('legacy "- JS" tab still present')
    if "- TS\n" not in s:
        fail('"- TS" tab missing')
    if "- UMD\n" not in s:
        fail('"- UMD" tab missing')

    # A page may have several {% list tabs %} blocks (e.g. a parameter-description
    # block plus the code-examples block); validate the one with the ```ts example.
    region, n_code = _tabs.code_region(s)
    if region is None:
        if n_code == 0:
            fail("no {% list tabs %} region with a ```ts example found")
        fail(f"expected exactly one tabs region with a ```ts example, found {n_code}")

    ts_blocks = _tabs.find_ts(region)
    if len(ts_blocks) != 1:
        fail(f"expected exactly one ```ts block in the code tabs region, found {len(ts_blocks)}")
    html_blocks = _tabs.find_html(region)
    if len(html_blocks) != 1:
        fail(f"expected exactly one ```html (UMD) block in the code tabs region, found {len(html_blocks)}")

    ts = textwrap.dedent(ts_blocks[0])
    html = textwrap.dedent(html_blocks[0])

    # first non-empty <script> (a library <script src=…> is empty and skipped)
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.DOTALL)
    umd_inner = next((sc for sc in scripts if sc.strip()), None)
    if umd_inner is None:
        fail("UMD html block found but it has no non-empty <script> with logic")

    for banned in FORBIDDEN:
        if banned in ts or banned in umd_inner:
            fail(f'forbidden token "{banned}" found in TS/UMD example')
    if "actions.v2." not in ts and "actions.v3." not in ts:
        fail("TS example does not use $b24.actions.v{2,3}.*")
    if "actions.v2." not in umd_inner and "actions.v3." not in umd_inner:
        fail("UMD example does not use $b24.actions.v{2,3}.*")

    return ts, umd_inner.strip("\n")


def ensure_project(proj):
    os.makedirs(proj, exist_ok=True)
    for fn in ("package.json", "package-lock.json"):
        shutil.copyfile(os.path.join(ENV_DIR, fn), os.path.join(proj, fn))
    # cache stamp covers BOTH files: editing package.json without re-locking
    # (or vice versa) must trigger a fresh install.
    h = hashlib.sha256()
    for fn in ("package-lock.json", "package.json"):
        with open(os.path.join(ENV_DIR, fn), "rb") as f:
            h.update(f.read())
    stamp = h.hexdigest()
    stamp_file = os.path.join(proj, ".lockstamp")
    fresh = False
    if os.path.isdir(os.path.join(proj, "node_modules")) and os.path.isfile(stamp_file):
        with open(stamp_file) as f:
            fresh = f.read().strip() == stamp
    if not fresh:
        print("[validate] npm ci (lockfile-pinned toolchain) ...", file=sys.stderr)
        subprocess.run(["npm", "ci", "--ignore-scripts"], cwd=proj,
                       check=True, timeout=NPM_TIMEOUT)
        with open(stamp_file, "w") as f:
            f.write(stamp)
    # tsconfig rationale: moduleResolution "bundler" matches the ESM browser-bundler
    # target (top-level await, no package "type":"module" needed); "dom" provides
    # `console`; skipLibCheck skips the SDK's own d.ts (it references node:stream).
    # strict still fully type-checks the example body (proven by tests).
    with open(os.path.join(proj, "tsconfig.json"), "w") as f:
        json.dump({
            "compilerOptions": {
                "target": "es2022", "module": "es2022", "moduleResolution": "bundler",
                "strict": True, "skipLibCheck": True, "noEmit": True,
                "lib": ["es2022", "dom"],
            },
            "files": ["example.ts"],
        }, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--project", default=os.path.join(HERE, ".tscheck"))
    a = ap.parse_args()

    abspath = os.path.abspath(a.path)
    if os.path.commonpath([abspath, REPO]) != REPO:
        fail(f"path is outside the repository: {abspath}")
    if not os.path.isfile(abspath):
        fail(f"file not found: {abspath}")

    ts, umd_js = extract(abspath)
    ensure_project(a.project)
    with open(os.path.join(a.project, "example.ts"), "w") as f:
        f.write(ts)
    with open(os.path.join(a.project, "umd_inner.js"), "w") as f:
        f.write(umd_js)

    ok = True
    tsc = os.path.join(a.project, "node_modules", ".bin", "tsc")
    r1 = subprocess.run([tsc, "-p", "tsconfig.json"], cwd=a.project,
                        capture_output=True, text=True, timeout=TSC_TIMEOUT)
    if r1.returncode != 0:
        ok = False
        print("TSC FAIL:\n" + r1.stdout + r1.stderr)
    else:
        print("TSC: OK")

    r2 = subprocess.run(["node", "--check", "umd_inner.js"], cwd=a.project,
                        capture_output=True, text=True, timeout=NODE_TIMEOUT)
    if r2.returncode != 0:
        ok = False
        print("NODE --check FAIL:\n" + r2.stdout + r2.stderr)
    else:
        print("NODE --check: OK")

    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
