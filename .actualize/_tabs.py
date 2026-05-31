"""Shared parsing of the {% list tabs %} regions and code blocks.

Single source of truth for the regexes so validate.py (which fails hard) and
record.py (which falls back gracefully) cannot drift apart. A page may carry
several {% list tabs %} blocks — parameter-description blocks plus one or more
code-example blocks; code_regions() returns every region that holds a ```ts
example, so each example can be validated independently.
"""
from __future__ import annotations

import re

TABS_RE = re.compile(r"\{%\s*list tabs\s*%\}(.*?)\{%\s*endlist\s*%\}", re.DOTALL)
TS_RE = re.compile(r"(?m)^[ \t]*```ts\n(.*?)\n[ \t]*```", re.DOTALL)
HTML_RE = re.compile(r"(?m)^[ \t]*```html\n(.*?)\n[ \t]*```", re.DOTALL)
METHOD_RE = re.compile(r"""method:\s*['"]([^'"]+)['"]""")


def tabs_region(text: str) -> str | None:
    """Inside of the first {% list tabs %}…{% endlist %}, or None.

    Prefer code_regions() when you specifically want the code-example block(s);
    this first-only helper is kept for record.py's graceful method-detection
    fallback, where any region (or even none) is acceptable.
    """
    m = TABS_RE.search(text)
    return m.group(1) if m else None


def code_regions(text: str) -> list[str]:
    """Inner text of every {% list tabs %} region holding a ```ts example, in order.

    A page may have several tabs blocks — parameter-description blocks (no code)
    plus one or more code-example blocks. Returning every code-bearing region lets
    callers validate each example. Empty list when no region carries a ```ts block.
    """
    return [r for r in TABS_RE.findall(text) if TS_RE.search(r)]


def find_ts(region: str) -> list[str]:
    return TS_RE.findall(region)


def find_html(region: str) -> list[str]:
    return HTML_RE.findall(region)


def first_method(scope: str) -> str | None:
    """First REST method name (single or double quoted) in scope, or None."""
    m = METHOD_RE.search(scope)
    return m.group(1) if m else None
