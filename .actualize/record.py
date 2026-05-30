#!/usr/bin/env python3
"""Maintain .actualize/ledger.tsv — one row per file (idempotent upsert).

Columns (TSV): date <TAB> file <TAB> sha256 <TAB> status <TAB> method

Usage:
  python3 .actualize/record.py <path-to-md> <status>   # upsert one file
  python3 .actualize/record.py --verify-all            # report sha256 drift
  python3 .actualize/record.py --verify <path-to-md>   # check one file

Upsert keeps a single row per file (latest wins), so re-runs do not create
duplicates; load() also de-duplicates on read, so a `merge=union` of parallel
PRs self-heals. Every cell is sanitized (no tab/newline) and the file is written
atomically (tmp + os.replace) to avoid a truncated ledger on interruption.
"""
import datetime
import hashlib
import os
import re
import sys

import _tabs

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LEDGER = os.path.join(HERE, "ledger.tsv")
HEADER = ["date", "file", "sha256", "status", "method"]
STATUS_LIMIT = 20


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def clean(value, limit=200):
    """Make a value safe for a single TSV cell."""
    return re.sub(r"[\t\r\n]+", " ", str(value)).strip()[:limit]


def detect_method(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    region = _tabs.tabs_region(text) or text
    ts = _tabs.find_ts(region)
    scope = ts[0] if ts else region
    return _tabs.first_method(scope) or os.path.basename(path)


def load():
    """Rows from the ledger, de-duplicated by file (last wins), sorted by file."""
    dedup = {}
    if os.path.exists(LEDGER):
        with open(LEDGER, encoding="utf-8") as f:
            for line in f.read().splitlines()[1:]:
                if not line.strip():
                    continue
                cells = line.split("\t")
                if len(cells) >= 2:
                    dedup[cells[1]] = cells
    return [dedup[k] for k in sorted(dedup)]


def save(rows):
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(clean(c) for c in r) + "\n")
    os.replace(tmp, LEDGER)


def rel(path):
    return os.path.relpath(os.path.abspath(path), REPO)


def upsert(path, status):
    abspath = os.path.abspath(path)
    if os.path.commonpath([abspath, REPO]) != REPO:
        print(f"ERROR: path is outside the repository: {abspath}")
        sys.exit(1)
    if clean(status) != clean(status, STATUS_LIMIT):
        print(f"WARNING: status truncated to {STATUS_LIMIT} chars", file=sys.stderr)
    r = rel(path)
    row = [
        datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        r, sha256(path), clean(status, STATUS_LIMIT), detect_method(path),
    ]
    rows = [x for x in load() if not (len(x) >= 2 and x[1] == r)]
    rows.append(row)
    rows.sort(key=lambda x: x[1])
    save(rows)
    print(f"recorded: {clean(r)} [{row[3]}] {row[2][:12]} {clean(row[4])}")


def verify(paths=None):
    rows = load()
    drift = 0
    for x in rows:
        if len(x) < 3:
            continue
        r, recorded = x[1], x[2]
        if paths and r not in paths:
            continue
        full = os.path.join(REPO, r)
        if not os.path.isfile(full):
            print(f"MISSING  {r}")
            drift += 1
            continue
        current = sha256(full)
        if current != recorded:
            print(f"DRIFT    {r}  recorded {recorded[:12]} != current {current[:12]}")
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
    elif args[0] == "--verify" and len(args) >= 2:
        verify(paths={rel(args[1])})
    elif len(args) >= 2:
        upsert(args[0], args[1])
    else:
        print("usage: record.py <path> <status> | --verify-all | --verify <path>")
        sys.exit(2)


if __name__ == "__main__":
    main()
