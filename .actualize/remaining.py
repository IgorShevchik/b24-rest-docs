#!/usr/bin/env python3
"""List/count documentation files that still use the deprecated jsSDK calls.

A file counts as "remaining" if it contains $b24.callMethod / $b24.callListMethod /
$b24.fetchListMethod (the deprecated jsSDK API in the "- JS" tab) AND is not yet
marked done/reviewed in .actualize/ledger.tsv. BX24.callMethod (the "- BX24.js"
tab) is intentionally NOT counted — it is left untouched.

Usage:
  python3 .actualize/remaining.py [root] [--list] [--limit N]

Defaults: root = api-reference
"""
import argparse
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LEDGER = os.path.join(HERE, "ledger.tsv")

LEGACY = re.compile(r"\$b24\.(callMethod|callListMethod|fetchListMethod)\b")
DONE = {"done", "reviewed"}


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
            if LEGACY.search(text):
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
