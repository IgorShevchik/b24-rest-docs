#!/usr/bin/env python3
"""Validate the b24jssdk TS + UMD examples inside a documentation .md file.

Checks (in order, cheapest first):
  1. structural: legacy "- JS" tab is gone, "- TS" and "- UMD" tabs are present;
  2. extraction: take the single ```ts block and the single UMD <script> from
     INSIDE the {% list tabs %} ... {% endlist %} region (not anywhere in the file);
  3. forbidden tokens: no callMethod / callListMethod / fetchListMethod /
     processResult / processData; an actions.v{2,3} call is present;
  4. types: `tsc --strict` against a PINNED @bitrix24/b24jssdk and PINNED typescript;
  5. syntax: `node --check` on the UMD inline script.

Usage:
  python3 .actualize/validate.py <path-to-md> [--project DIR]

Exit code 0 = PASS, non-zero = FAIL. The pinned versions below make validation
reproducible; bump them deliberately when the documented SDK target changes.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# Pinned for reproducible validation. Keep SDK_VERSION aligned with the version
# referenced in the UMD <script> tag of the examples.
SDK_VERSION = "1.2.0"
TS_VERSION = "5.7.3"

FORBIDDEN = ["callMethod", "callListMethod", "fetchListMethod",
             "processResult", "processData"]


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def extract(md_path):
    """Return (ts_code, umd_inner_js) extracted from inside the tabs region."""
    s = open(md_path, encoding="utf-8").read()

    # structural checks on the whole file
    if "- JS\n" in s:
        fail('legacy "- JS" tab still present')
    if "- TS\n" not in s:
        fail('"- TS" tab missing')
    if "- UMD\n" not in s:
        fail('"- UMD" tab missing')

    m = re.search(r"\{%\s*list tabs\s*%\}(.*?)\{%\s*endlist\s*%\}", s, re.DOTALL)
    if not m:
        fail("no {% list tabs %} ... {% endlist %} region found")
    region = m.group(1)

    ts_blocks = re.findall(r"(?m)^[ \t]*```ts\n(.*?)\n[ \t]*```", region, re.DOTALL)
    if len(ts_blocks) != 1:
        fail(f"expected exactly one ```ts block in tabs, found {len(ts_blocks)}")
    html_blocks = re.findall(r"(?m)^[ \t]*```html\n(.*?)\n[ \t]*```", region, re.DOTALL)
    if len(html_blocks) != 1:
        fail(f"expected exactly one ```html (UMD) block in tabs, found {len(html_blocks)}")

    ts = textwrap.dedent(ts_blocks[0])
    html = textwrap.dedent(html_blocks[0])

    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.DOTALL)
    umd_inner = next((sc for sc in scripts if sc.strip()), None)
    if umd_inner is None:
        fail("UMD html block found but it has no non-empty <script> with logic")

    # forbidden / required tokens
    for banned in FORBIDDEN:
        if banned in ts or banned in umd_inner:
            fail(f'forbidden token "{banned}" found in TS/UMD example')
    if "actions.v2." not in ts and "actions.v3." not in ts:
        fail("TS example does not use $b24.actions.v{2,3}.*")

    return ts, umd_inner.strip("\n")


def ensure_project(proj):
    os.makedirs(proj, exist_ok=True)
    sdk_pkg = os.path.join(proj, "node_modules", "@bitrix24", "b24jssdk", "package.json")
    tsc_bin = os.path.join(proj, "node_modules", ".bin", "tsc")
    need = not (os.path.isfile(sdk_pkg) and os.path.isfile(tsc_bin))
    if not need:
        try:
            if json.load(open(sdk_pkg))["version"] != SDK_VERSION:
                need = True
        except Exception:
            need = True
    if need:
        with open(os.path.join(proj, "package.json"), "w") as f:
            json.dump({"name": "b24-tscheck", "private": True, "type": "module"}, f)
        print(f"[validate] installing @bitrix24/b24jssdk@{SDK_VERSION} + "
              f"typescript@{TS_VERSION} ...", file=sys.stderr)
        subprocess.run(
            ["npm", "i", "--no-save", "--ignore-scripts",
             f"@bitrix24/b24jssdk@{SDK_VERSION}", f"typescript@{TS_VERSION}"],
            cwd=proj, check=True,
        )
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
    open(os.path.join(a.project, "example.ts"), "w").write(ts)
    open(os.path.join(a.project, "umd_inner.js"), "w").write(umd_js)

    ok = True
    tsc = os.path.join(a.project, "node_modules", ".bin", "tsc")
    r1 = subprocess.run([tsc, "-p", "tsconfig.json"], cwd=a.project,
                        capture_output=True, text=True)
    if r1.returncode != 0:
        ok = False
        print("TSC FAIL:\n" + r1.stdout + r1.stderr)
    else:
        print("TSC: OK")

    r2 = subprocess.run(["node", "--check", "umd_inner.js"], cwd=a.project,
                        capture_output=True, text=True)
    if r2.returncode != 0:
        ok = False
        print("NODE --check FAIL:\n" + r2.stdout + r2.stderr)
    else:
        print("NODE --check: OK")

    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
