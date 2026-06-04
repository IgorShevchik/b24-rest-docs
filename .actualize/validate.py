#!/usr/bin/env python3
"""Validate the b24jssdk TS + UMD examples inside a documentation .md file.

Checks (cheapest first):
  1. structural: legacy "- JS" tab is gone, "- TS" and "- UMD" tabs are present;
  2. extraction: from EVERY {% list tabs %} … {% endlist %} region that holds a
     ```ts example (a page may have several code-example blocks), take the single
     ```ts block and the single UMD <script> — each example is validated, not
     blocks found anywhere else on the page;
  3. forbidden tokens: no callMethod / callListMethod / fetchListMethod /
     processResult / processData; an actions.v{2,3} call is present in BOTH tabs;
  3b. template uniformity: the mandatory comments (success-guard, UMD init, catch,
      Shape-of-payload before the main result type) are present and `requestId`
      carries no trailing comma — see PROMPT.md "Code style (mandatory)";
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

# Mandatory template comments — the verified canon (see PROMPT.md "JS (TS) tab" / "JS (UMD) tab").
# Enforced structurally so the corpus cannot drift; a unit test keeps them in sync with PROMPT.md.
GUARD_COMMENT = "// The payload is available only on a successful response"
INIT_COMMENT = "// Initialize the SDK inside a Bitrix24 frame"
CATCH_COMMENT = "// Thrown on transport or SDK failures (AjaxError, SdkError, etc.)"
SHAPE_COMMENT = "// Shape of the payload returned in result"
# The Shape comment has two accepted forms: the object form (SHAPE_COMMENT, "… the payload …") and,
# for list methods, an element form ("// Shape of each <item> returned in result[]"). The text
# between "Shape of" and "returned in result" is free; the trailing `\b` anchors on the word
# "result" so typos ("results", "resulting") are rejected while every real tail (".task", "[]",
# " (parenthetical)", " array") still passes. Both forms are good docs; the check accepts either.
SHAPE_RE = re.compile(r"// Shape of .+ returned in (?:the )?result\b")

MAX_MD_BYTES = 2_000_000  # guard: a method page is never this big; refuse pathological input


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def extract(md_path):
    """Return [(ts_code, umd_inner_js), …] — one pair per code-example tabs region.

    A page may have several {% list tabs %} blocks (parameter-description blocks
    plus one or more code-example blocks); every region holding a ```ts example is
    validated and returned, so the caller can type-check each one independently.
    """
    size = os.path.getsize(md_path)
    if size > MAX_MD_BYTES:
        fail(f"file too large: {size} bytes (limit {MAX_MD_BYTES})")
    with open(md_path, encoding="utf-8") as f:
        s = f.read().replace("\r\n", "\n")  # normalise CRLF so the fence regexes match

    if "- JS\n" in s:
        fail('legacy "- JS" tab still present')
    # Canonical tab labels are "JS (TS)" / "JS (UMD)" (doc-team convention). The older
    # "- TS" / "- UMD" labels are still accepted during the transition (existing pages get
    # renamed upstream and synced back); tighten to canonical-only once that sync lands.
    if "- JS (TS)\n" not in s and "- TS\n" not in s:
        fail('"JS (TS)" tab missing')
    if "- JS (UMD)\n" not in s and "- UMD\n" not in s:
        fail('"JS (UMD)" tab missing')

    regions = _tabs.code_regions(s)
    if not regions:
        fail("no {% list tabs %} region with a ```ts example found")

    return [_extract_region(r, i, len(regions)) for i, r in enumerate(regions, 1)]


def _prev_nonblank(lines, i):
    j = i - 1
    while j >= 0 and not lines[j].strip():
        j -= 1
    return lines[j].strip() if j >= 0 else ""


def _next_nonblank(lines, i):
    j = i + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    return lines[j].strip() if j < len(lines) else ""


def style_errors(code):
    """Template-uniformity lints over one code example (TS or UMD inner JS).

    The mandatory comments and the no-trailing-comma-after-`requestId` canon are
    enforced structurally so the corpus cannot drift (see PROMPT.md "Code style").
    Helper types (not used as a `.make<X>` generic) are exempt from the Shape comment.
    Returns a list of human-readable violation strings (empty == clean).
    """
    errs = []
    lines = code.split("\n")
    # match call/callList/fetchList.make<X> AND the list-generic make<X[]> (element type is X)
    main_types = {g.removesuffix("[]")
                  for g in re.findall(r"\.make<(\w+(?:\[\])?)>", code)}
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "if (!response.isSuccess) {" and _prev_nonblank(lines, i) != GUARD_COMMENT:
            errs.append(f"missing `{GUARD_COMMENT}` before `if (!response.isSuccess)`")
        if (s.startswith("const $b24") and "B24Js.initializeB24Frame()" in s
                and _prev_nonblank(lines, i) != INIT_COMMENT):
            errs.append(f"missing `{INIT_COMMENT}` before `initializeB24Frame()`")
        if s == "} catch (error) {" and _next_nonblank(lines, i) != CATCH_COMMENT:
            errs.append(f"missing `{CATCH_COMMENT}` as the first line of the catch block")
        m = re.match(r"type (\w+) =", s)
        if m and m.group(1) in main_types and not SHAPE_RE.search(_prev_nonblank(lines, i)):
            errs.append(f"missing the `// Shape of … returned in result` comment before the main "
                        f"result type `{m.group(1)}` — object form `{SHAPE_COMMENT} (…)`, "
                        f"list form `// Shape of each <item> returned in result[]`")
        if "getUuidRfc4122()," in s:
            errs.append("trailing comma after `requestId` (drop it — it is the last property "
                        "of the call.make({…}) argument)")
    return errs


def _extract_region(region, idx, total):
    """Validate one code-example region and return its (ts_code, umd_inner_js)."""
    where = f"code region {idx}/{total}"
    ts_blocks = _tabs.find_ts(region)
    if len(ts_blocks) != 1:
        fail(f"expected exactly one ```ts block in {where}, found {len(ts_blocks)}")
    html_blocks = _tabs.find_html(region)
    if len(html_blocks) != 1:
        fail(f"expected exactly one ```html (UMD) block in {where}, found {len(html_blocks)}")

    ts = textwrap.dedent(ts_blocks[0])
    html = textwrap.dedent(html_blocks[0])

    # first non-empty <script> (a library <script src=…> is empty and skipped)
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.DOTALL)
    umd_inner = next((sc for sc in scripts if sc.strip()), None)
    if umd_inner is None:
        fail(f"UMD html block in {where} has no non-empty <script> with logic")

    for banned in FORBIDDEN:
        if banned in ts or banned in umd_inner:
            fail(f'forbidden token "{banned}" found in {where}')
    if "actions.v2." not in ts and "actions.v3." not in ts:
        fail(f"TS example in {where} does not use $b24.actions.v{{2,3}}.*")
    if "actions.v2." not in umd_inner and "actions.v3." not in umd_inner:
        fail(f"UMD example in {where} does not use $b24.actions.v{{2,3}}.*")

    style = style_errors(ts) + style_errors(umd_inner)
    if style:
        fail(f"code-style/comment violations in {where}:\n"
             + "\n".join(f"  - {e}" for e in style))

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

    examples = extract(abspath)
    ensure_project(a.project)
    tsc = os.path.join(a.project, "node_modules", ".bin", "tsc")
    total = len(examples)

    # Compile each code example separately (overwriting example.ts / umd_inner.js):
    # examples are independent ES modules, so isolating them keeps errors attributable.
    ok = True
    for i, (ts, umd_js) in enumerate(examples, 1):
        tag = f"[example {i}/{total}]"
        with open(os.path.join(a.project, "example.ts"), "w") as f:
            f.write(ts)
        with open(os.path.join(a.project, "umd_inner.js"), "w") as f:
            f.write(umd_js)

        r1 = subprocess.run([tsc, "-p", "tsconfig.json"], cwd=a.project,
                            capture_output=True, text=True, timeout=TSC_TIMEOUT)
        if r1.returncode != 0:
            ok = False
            print(f"TSC FAIL {tag}:\n" + r1.stdout + r1.stderr)
        else:
            print(f"TSC OK {tag}")

        r2 = subprocess.run(["node", "--check", "umd_inner.js"], cwd=a.project,
                            capture_output=True, text=True, timeout=NODE_TIMEOUT)
        if r2.returncode != 0:
            ok = False
            print(f"NODE --check FAIL {tag}:\n" + r2.stdout + r2.stderr)
        else:
            print(f"NODE --check OK {tag}")

    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
