#!/usr/bin/env python3
"""List/count documentation files that still ship deprecated jsSDK examples.

A file counts as "remaining" if it is NOT yet marked done/reviewed in
.actualize/ledger.tsv AND shows either deprecation signal (see is_legacy()):
  - a deprecated $b24.callMethod / $b24.callListMethod / $b24.fetchListMethod call, or
  - a combined legacy "- JS" tab inside a {% list tabs %} region — the same signal
    validate.py gates on. The tab signal catches pages whose call style the regex
    misses (e.g. B24.callMethod) — the blind spot that let a legacy page slip past the
    drain (sale/business-value-person-domain-add) while remaining.py reported it done.
BX24.callMethod (the kept "- BX24.js" tab) and the actualized "- JS (TS)" / "- JS (UMD)"
tabs are NOT counted.

Usage:
  python3 .actualize/remaining.py [root] [--list] [--limit N]

Defaults: root = api-reference
"""
import argparse
import os
import re

import _tabs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LEDGER = os.path.join(HERE, "ledger.tsv")

LEGACY = re.compile(r"\$b24\.(callMethod|callListMethod|fetchListMethod)\b")
DONE = {"done", "reviewed"}


def _has_legacy_js_tab(text):
    """True iff a combined legacy "- JS" tab appears inside a {% list tabs %} region.

    Mirrors validate.py: an actualized page uses "- JS (TS)" / "- JS (UMD)", so a bare
    "- JS" tab label only survives on a page that was never converted. A prose "- JS"
    bullet outside any tabs region must not count, hence the region scoping.
    """
    return any("- JS\n" in region for region in _tabs.TABS_RE.findall(text))


def is_legacy(text):
    """True iff the page still ships deprecated jsSDK examples (union of two signals).

    Broaden, never narrow: a deprecated $b24.call* (LEGACY) OR a legacy "- JS" tab. The
    tab signal closes the blind spot where a legacy tab used a call style LEGACY misses
    (e.g. B24.callMethod), so the drain never picked the page up.
    """
    return bool(LEGACY.search(text)) or _has_legacy_js_tab(text)


def done_set():
    done = set()
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as f:
            for line in f.read().splitlines()[1:]:
                parts = line.split("\t")
                if len(parts) >= 4 and parts[3] in DONE:
                    done.add(parts[1])
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default="api-reference")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    done = done_set()
    remaining, already = [], 0
    root = os.path.join(REPO, a.root)
    for dirpath, _, files in os.walk(root):
        for name in files:
            if not name.endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, REPO)
            try:
                with open(full, encoding="utf-8") as fh:
                    text = fh.read()
            except (OSError, UnicodeDecodeError):
                continue
            if is_legacy(text):
                if rel in done:
                    already += 1
                else:
                    remaining.append(rel)

    remaining.sort()
    print(f"root: {a.root}")
    print(f"remaining (legacy jsSDK, not done): {len(remaining)}")
    print(f"already done/reviewed (still match legacy regex): {already}")
    if a.list or a.limit:
        shown = remaining[: a.limit] if a.limit else remaining
        for r in shown:
            print(r)
        if a.limit and len(remaining) > a.limit:
            print(f"... (+{len(remaining) - a.limit} more)")


if __name__ == "__main__":
    main()
