"""Shared parsing of the {% list tabs %} region and code blocks.

Single source of truth for the regexes so validate.py (which fails hard) and
record.py (which falls back gracefully) cannot drift apart. A page may carry several
{% list tabs %} blocks (e.g. a parameter-description block plus the code-examples
block); code_region() returns the one holding the ```ts example.
"""
import re

TABS_RE = re.compile(r"\{%\s*list tabs\s*%\}(.*?)\{%\s*endlist\s*%\}", re.DOTALL)
TS_RE = re.compile(r"(?m)^[ \t]*```ts\n(.*?)\n[ \t]*```", re.DOTALL)
HTML_RE = re.compile(r"(?m)^[ \t]*```html\n(.*?)\n[ \t]*```", re.DOTALL)
METHOD_RE = re.compile(r"""method:\s*['"]([^'"]+)['"]""")


def tabs_region(text):
    """Return the inside of the first {% list tabs %}…{% endlist %}, or None."""
    m = TABS_RE.search(text)
    return m.group(1) if m else None


def tabs_regions(text):
    """Inside of every {% list tabs %}…{% endlist %} region, in document order."""
    return TABS_RE.findall(text)


def code_region(text):
    """Return (region, count) for the tabs region holding a ```ts example.

    Pages may have several {% list tabs %} blocks (e.g. a parameter-description
    block plus the code-examples block). The example lives in the region with a
    ```ts fence. `region` is that region's inner text, or None when zero or more
    than one region carries a ```ts block; `count` is how many did (for messages).
    """
    with_ts = [r for r in TABS_RE.findall(text) if TS_RE.search(r)]
    return (with_ts[0] if len(with_ts) == 1 else None), len(with_ts)


def find_ts(region):
    return TS_RE.findall(region)


def find_html(region):
    return HTML_RE.findall(region)


def first_method(scope):
    """First REST method name (single or double quoted) in scope, or None."""
    m = METHOD_RE.search(scope)
    return m.group(1) if m else None
