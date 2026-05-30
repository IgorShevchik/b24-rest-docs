#!/usr/bin/env python3
"""Maintain .actualize/ledger.tsv — one row per file (idempotent upsert).

Columns (TSV): date <TAB> file <TAB> sha256 <TAB> status <TAB> method

Usage:
  python3 .actualize/record.py <path-to-md> <status>   # upsert one file
  python3 .actualize/record.py --verify-all            # report sha256 drift
  python3 .actualize/record.py --verify <path-to-md>   # check one file

Upsert keeps a single row per file (latest wins), so re-runs do not create
duplicates and the ledger stays a clean source of truth. The sha256 is over the
whole file, so post-processing edits can be detected as drift.
"""
import datetime
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LEDGER = os.path.join(HERE, "ledger.tsv")
HEADER = ["date", "file", "sha256", "status", "method"]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def clean(value, limit=120):
    """Make a value safe for a TSV cell."""
    value = re.sub(r"[\t\r\n]+", " ", str(value)).strip()
    return value[:limit]


def detect_method(path):
    text = open(path, encoding="utf-8").read()
    m = re.search(r"\{%\s*list tabs\s*%\}(.*?)\{%\s*endlist\s*%\}", text, re.DOTALL)
    region = m.group(1) if m else text
    tsm = re.search(r"```ts\n(.*?)\n[ \t]*```", region, re.DOTALL)
    scope = tsm.group(1) if tsm else region
    mm = re.search(r"method:\s*'([^']+)'", scope)
    return mm.group(1) if mm else os.path.basename(path)


def load():
    rows = []
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for line in lines[1:]:
            if line.strip():
                rows.append(line.split("\t"))
    return rows


def save(rows):
    with open(LEDGER, "w", encoding="utf-8") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


def rel(path):
    return os.path.relpath(os.path.abspath(path), REPO)


def upsert(path, status):
    r = rel(path)
    row = [
        datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        r, sha256(path), clean(status, 20), clean(detect_method(path)),
    ]
    rows = [x for x in load() if not (len(x) >= 2 and x[1] == r)]
    rows.append(row)
    rows.sort(key=lambda x: x[1])
    save(rows)
    print(f"recorded: {r} [{row[3]}] {row[2][:12]} {row[4]}")


def verify(paths=None):
    rows = load()
    drift = 0
    for x in rows:
        if len(x) < 3:
            continue
        date, r, recorded = x[0], x[1], x[2]
        if paths and r not in paths:
            continue
        full = os.path.join(REPO, r)
        if not os.path.isfile(full):
            print(f"MISSING  {r}")
            drift += 1
            continue
        cur = sha256(full)
        if cur != recorded:
            print(f"DRIFT    {r}  recorded {recorded[:12]} != current {cur[:12]}")
            drift += 1
        else:
            print(f"OK       {r}")
    print(f"--- {len(rows)} tracked, {drift} drifted/missing ---")
    sys.exit(1 if drift else 0)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if args[0] == "--verify-all":
        verify()
    elif args[0] == "--verify":
        verify(paths={rel(args[1])})
    elif len(args) >= 2:
        upsert(args[0], args[1])
    else:
        print("usage: record.py <path> <status> | --verify-all | --verify <path>")
        sys.exit(2)


if __name__ == "__main__":
    main()
