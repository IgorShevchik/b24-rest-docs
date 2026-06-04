#!/usr/bin/env python3
"""Validate the b24jssdk TS + UMD examples inside a documentation .md file.

Checks (cheapest first):
  1. structural: the legacy combined "- JS" tab is gone (checked only inside
     {% list tabs %} regions, never prose) and "JS (TS)"/"JS (UMD)" tabs are present
     (legacy "- TS"/"- UMD" still accepted during the upstream rename);
  2. extraction: from EVERY {% list tabs %} … {% endlist %} region that holds a
     ```ts example (a page may have several code-example blocks), take the single
     ```ts block and the single UMD <script> — each example is validated, not
     blocks found anywhere else on the page;
  3. forbidden tokens: no callMethod / callListMethod / fetchListMethod /
     processResult / processData; an actions.v{2,3} call is present in BOTH tabs;
  3b. template uniformity: the mandatory comments (success-guard, UMD init, catch,
      Shape-of-payload before the main result type) are present and `requestId`
      carries no trailing comma — see PROMPT.md "Code style (mandatory)";
  3c. field/method cross-check: the self-declared result type is confronted with the
      PAGE itself (not just with itself, the gap tsc cannot see) — the SDK `method:`
      must match the cURL `/rest/.../<method>` endpoint, and every result-type field
      must be documented in a JSON example or a `#| … |#` table (see cross_check());
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

# Every `.make<…>` generic on the page (inner text up to the first `>`). main_result_types()
# keeps the simple named ones; shape_coverage() surfaces the rest so none is silently skipped.
MAKE_RE = re.compile(r"\.make<([^>]+)>")

MAX_MD_BYTES = 2_000_000  # guard: a method page is never this big; refuse pathological input

# --- field/method cross-checks (the "self-declared-type blind spot" guard) -----------
# tsc only proves the example compiles against the type the agent wrote in the SAME file;
# it never confronts that type with the real API. These checks confront it with the PAGE:
#   - method: the cURL/PHP/etc. tabs are out of scope for the agent (PROMPT rule 3), so the
#     `/rest/.../<method>` endpoint is an INDEPENDENT source of truth for the REST method;
#   - fields: the JSON response example(s) + the bold field names in the `#| … |#` tables
#     are the documented field universe. A result-type key absent from ALL of it is a strong
#     hallucination signal (deliberately a generous superset => near-zero false positives).
REST_URL_RE = re.compile(r"/rest/(?:[^\s/'\"]+/)*([A-Za-z][\w.]*?)(?:\.json)?(?=[\s'\"?]|$)")
JSON_BLOCK_RE = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
JSON_KEY_RE = re.compile(r'"([A-Za-z_]\w*)"\s*:')
TABLE_FIELD_RE = re.compile(r"\|\|\s*\*\*([A-Za-z_]\w*)\*?\*\*")
TYPE_OPEN_RE = re.compile(r"^\s*type\s+\w+\s*=\s*\{")
PROP_KEY_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*\??\s*:")
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script>", re.DOTALL)


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def _has_legacy_js_tab(s):
    """True iff a legacy combined "- JS" tab label appears INSIDE a {% list tabs %} region.
    A prose "- JS" bullet elsewhere on the page must not count (it would be a false failure)."""
    return any("- JS\n" in region for region in _tabs.TABS_RE.findall(s))


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

    if _has_legacy_js_tab(s):
        fail('legacy "- JS" tab still present')
    # Canonical tab labels are "JS (TS)" / "JS (UMD)" (doc-team convention). The rename has landed
    # (corpus: 134 "- JS (TS)" pages, 0 legacy "- TS"); the older "- TS" / "- UMD" labels are kept
    # accepted only as a thin safety margin. Tightening to canonical-only is the remaining §8 step.
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


def main_result_types(code):
    """Element type names taken from every `.make<X>` / `.make<X[]>` generic in the code.

    Returns only simple word-char generics (`\\w+`, optional `[]`); inline-literal or multi-type
    generics (make<{…}>, make<Foo, Bar>) are excluded. A primitive like `number` (from make<number[]>)
    does pass the `\\w+` filter and is returned, but it can never have a local `type number =`, so the
    Shape lint in style_errors() is a no-op for it; shape_coverage() reports such generics explicitly.
    """
    out = set()
    for g in MAKE_RE.findall(code):
        base = g.strip().removesuffix("[]").strip()
        if re.fullmatch(r"\w+", base):
            out.add(base)
    return out


def shape_coverage(code):
    """(checked, uncovered) for one TS example.

    checked   — named main types with a local `type X =` (the Shape comment is enforced on these);
    uncovered — make<…> generics with no local alias (inline literal / primitive / external) that
    the Shape check cannot key on. Reported, never failed — so the silent-skip that hid the
    list-generic bug is visible at a glance.
    """
    declared = set(re.findall(r"(?m)^\s*type (\w+) =", code))
    checked, uncovered = set(), []
    for g in MAKE_RE.findall(code):
        base = g.strip().removesuffix("[]").strip()
        if re.fullmatch(r"\w+", base) and base in declared:
            checked.add(base)
        else:
            uncovered.append(g.strip())
    return checked, uncovered


def style_errors(code):
    """Template-uniformity lints over one code example (TS or UMD inner JS).

    The mandatory comments and the no-trailing-comma-after-`requestId` canon are
    enforced structurally so the corpus cannot drift (see PROMPT.md "Code style").
    Helper types (not used as a `.make<X>` generic) are exempt from the Shape comment.
    Returns a list of human-readable violation strings (empty == clean).
    """
    errs = []
    lines = code.split("\n")
    main_types = main_result_types(code)  # simple named make<X> / make<X[]> element types
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


def curl_methods(region):
    """REST method name(s) from the cURL `/rest/.../<method>` URLs in a tabs region.

    Webhook (`/rest/<id>/<webhook>/<method>`) and OAuth (`/rest/<method>`) forms both
    encode the same method as the final path segment; a trailing `.json` is stripped.
    Returns a set (normally one element — both cURL tabs name the same method).
    """
    return set(REST_URL_RE.findall(region))


def umd_inner_js(html_block):
    """First non-empty <script> body in a UMD html block ('' if none)."""
    scripts = SCRIPT_RE.findall(html_block)
    return next((sc for sc in scripts if sc.strip()), "")


def type_body_keys(ts):
    """Property key names declared inside every `type X = { … }` block in the TS code.

    A brace-depth walk scopes extraction to result-type declarations, so request-side
    keys (the `params: { … }` / `call.make({ … })` arguments) are never collected. Nested
    keys on their own line are included; an inline `{ k: v }` on a property line yields the
    outer key only (a false NEGATIVE at worst — never a false positive that fails a page).
    Returns a set.
    """
    keys, depth, in_type = set(), 0, False
    for line in ts.split("\n"):
        if not in_type:
            if TYPE_OPEN_RE.search(line):
                depth = line.count("{") - line.count("}")
                in_type = depth > 0
            continue
        m = PROP_KEY_RE.match(line)
        if m:
            keys.add(m.group(1))
        depth += line.count("{") - line.count("}")
        if depth <= 0:
            in_type = False
    return keys


def documented_field_names(page_text):
    """Every field name documented anywhere on the page — the field universe.

    Keys of all ```json blocks (success + error response examples) plus the bold field
    names in the `#| … |#` tables. Deliberately a GENEROUS superset (request params and
    response fields together): the cross-check only asserts result-type keys are a SUBSET
    of this, so extra names lower false positives while a truly invented key is still caught.
    """
    names = set()
    for block in JSON_BLOCK_RE.findall(page_text):
        names |= set(JSON_KEY_RE.findall(block))
    names |= set(TABLE_FIELD_RE.findall(page_text))
    return names


def cross_check(page_text):
    """Field/method cross-check for one page → (errors, notes).

    errors gate the page (non-empty == FAIL); notes are advisory (printed, never fail).

    Method (gate) — per code-example region, the SDK `method:` in the TS and UMD tabs must
    equal each other and the cURL `/rest/.../<method>` endpoint in that same region (when one
    is present). Fields (gate) — every `type` key across the page's examples must appear in the
    documented field universe (a JSON example or a `#| … |#` table).

    A gate needs a reference to have authority: when the page documents NO response fields at
    all (empty universe — e.g. a widget/placement tutorial with no "response handling" section),
    the type cannot be grounded, so any keys are reported as a note instead of failing — a page
    that is structurally impossible to satisfy must not brick the batch. Real method pages (all
    of crm) carry a response section, so their result types still gate hard. See the module header.
    """
    errors, notes = [], []
    universe = documented_field_names(page_text)
    type_keys = set()
    for idx, region in enumerate(_tabs.code_regions(page_text), 1):
        ts_blocks = _tabs.find_ts(region)
        html_blocks = _tabs.find_html(region)
        ts_code = textwrap.dedent(ts_blocks[0]) if ts_blocks else ""
        umd = umd_inner_js(html_blocks[0]) if html_blocks else ""
        ts_m = _tabs.first_method(ts_code)
        umd_m = _tabs.first_method(umd)
        curls = curl_methods(region)
        if ts_m and umd_m and ts_m != umd_m:
            errors.append(f"code region {idx}: method mismatch — TS `{ts_m}` vs UMD `{umd_m}`")
        sdk_m = ts_m or umd_m
        if sdk_m and curls and sdk_m not in curls:
            errors.append(f"code region {idx}: SDK method `{sdk_m}` is not the cURL endpoint "
                          f"{{{', '.join(sorted(curls))}}} documented on the page")
        type_keys |= type_body_keys(ts_code)
    ungrounded = sorted(type_keys - universe)
    if ungrounded:
        if universe:
            errors.append("result-type field(s) documented nowhere on the page (not in any JSON "
                          f"example or `#| … |#` table) — likely invented: {', '.join(ungrounded)}")
        else:
            notes.append("page documents no response fields (no JSON example or field table); "
                         f"result-type field(s) are ungrounded guesses: {', '.join(ungrounded)}")
    return errors, notes


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
    umd_inner = umd_inner_js(html) or None
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

    # Observability: report what the Shape check actually saw, so a future regex gap (like the
    # list-generic one this hardening followed) cannot silently check nothing again.
    checked, uncovered = set(), []
    for ts, _ in examples:
        c, u = shape_coverage(ts)
        checked |= c
        uncovered += u
    print(f"[validate] Shape: {len(checked)} named result type(s) checked"
          + (f" ({', '.join(sorted(checked))})" if checked else ""), file=sys.stderr)
    if uncovered:
        print("[validate] note: make<…> generic(s) with no local type alias "
              f"(Shape check N/A): {', '.join(uncovered)}", file=sys.stderr)

    # Field/method cross-check: confront the self-declared type with the PAGE (cURL endpoint
    # + JSON response + field tables), not just with itself — the gap tsc cannot see.
    with open(abspath, encoding="utf-8") as f:
        page_text = f.read().replace("\r\n", "\n")
    xerrs, xnotes = cross_check(page_text)
    for n in xnotes:
        print(f"[validate] note: {n}", file=sys.stderr)
    if xerrs:
        fail("field/method cross-check failed (the example disagrees with the page):\n"
             + "\n".join(f"  - {e}" for e in xerrs))
    field_status = "see field note(s) above" if xnotes else "result-type fields documented on the page"
    print(f"[validate] cross-check: method(s) match the cURL endpoint; {field_status}",
          file=sys.stderr)

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
